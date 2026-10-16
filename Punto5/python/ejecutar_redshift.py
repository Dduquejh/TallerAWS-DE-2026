
import json
import time
import re
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


# Configuracion del taller
REGION = "us-east-2"
NAMESPACE = "taller-redshift-ns"
WORKGROUP = "taller-redshift-wg"
DATABASE = "taller_dw"
SECRET_NAME = "taller/redshift/admin"

ROLE_ARN = (
    "arn:aws:iam::573992724610:role/RedshiftS3ReadRole"
)

ACCOUNT_ID = boto3.client(
    "sts", region_name=REGION
).get_caller_identity()["Account"]

BUCKET = f"talleraws-redshift-{ACCOUNT_ID}"
DATA_PREFIX = "datos/"

DATA_DIR = Path(__file__).resolve().parent.parent / "datos"
FILES = ["clientes.csv", "ventas.csv"]


def preparar_s3():
    """Crear el bucket si no existe y subir los CSV."""
    s3 = boto3.client("s3", region_name=REGION)

    try:
        s3.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={
                "LocationConstraint": REGION
            },
        )
        print(f"Bucket creado: {BUCKET}")

    except ClientError as error:
        code = error.response["Error"]["Code"]

        if code not in ("BucketAlreadyOwnedByYou",):
            raise

        print(f"Bucket existente: {BUCKET}")

    for filename in FILES:
        path = DATA_DIR / filename

        if not path.is_file():
            raise FileNotFoundError(
                f"No se encontro el archivo: {path}"
            )

        key = f"{DATA_PREFIX}{filename}"

        s3.upload_file(str(path), BUCKET, key)

        s3.head_object(Bucket=BUCKET, Key=key)

        print(f"Subido y verificado: s3://{BUCKET}/{key}")


def obtener_clientes_aws():
    """Preparar los clientes de Redshift Data API y Secrets Manager."""
    secrets = boto3.client(
        "secretsmanager", region_name=REGION
    )
    redshift = boto3.client(
        "redshift-serverless", region_name=REGION
    )
    data = boto3.client(
        "redshift-data", region_name=REGION
    )

    # Verificar que el secreto existe, sin leer ni imprimir
    # su contraseña.
    secret_arn = secrets.describe_secret(
        SecretId=SECRET_NAME
    )["ARN"]

    namespace = redshift.get_namespace(
        namespaceName=NAMESPACE
    )["namespace"]

    if namespace["status"] != "AVAILABLE":
        raise RuntimeError(
            f"Namespace no disponible: {namespace['status']}"
        )

    workgroup = redshift.get_workgroup(
        workgroupName=WORKGROUP
    )["workgroup"]

    if workgroup["status"] != "AVAILABLE":
        raise RuntimeError(
            f"Workgroup no disponible: {workgroup['status']}"
        )

    associated_roles = []

    for role in namespace.get("iamRoles", []):
        if isinstance(role, dict):
            arn = role.get("iamRoleArn", "")
        elif isinstance(role, str):
            if role.startswith("arn:"):
                arn = role
            else:
                match = re.search(r"iamRoleArn=(arn:[^,\s)]+)", role)
                arn = match.group(1) if match else ""
        else:
            arn = ""

        if arn:
            associated_roles.append(arn)

    if ROLE_ARN not in associated_roles:
        raise RuntimeError(
            f"El rol IAM de S3 no esta asociado al namespace. "
            f"Roles encontrados: {associated_roles}"
        )

    return data, secret_arn


def esperar_sentencia(data, statement_id):
    """Esperar la ejecucion y detectar errores."""
    while True:
        result = data.describe_statement(Id=statement_id)
        status = result["Status"]

        if status == "FINISHED":
            print(f"Sentencia terminada: {statement_id}")
            return result

        if status in ("FAILED", "ABORTED"):
            raise RuntimeError(
                f"Sentencia {status}: {result.get('Error', 'Error desconocido')}"
            )

        time.sleep(2)


def ejecutar_sql(data, secret_arn, sql, recuperar=False):
    """Enviar SQL por Data API y recuperar resultados opcionales."""
    response = data.execute_statement(
        WorkgroupName=WORKGROUP,
        Database=DATABASE,
        SecretArn=secret_arn,
        Sql=sql,
    )

    statement_id = response["Id"]
    print(f"SQL enviado. ID: {statement_id}")

    esperar_sentencia(data, statement_id)

    if recuperar:
        return obtener_resultados(data, statement_id)

    return None


def obtener_resultados(data, statement_id):
    """Convertir los registros de Data API a filas imprimibles."""
    response = data.get_statement_result(Id=statement_id)

    columns = [
        column["name"]
        for column in response["ColumnMetadata"]
    ]

    rows = []

    for record in response["Records"]:
        row = []

        for field in record:
            if field.get("isNull"):
                row.append(None)
            else:
                value = next(
                    (
                        field[key]
                        for key in (
                            "stringValue",
                            "longValue",
                            "doubleValue",
                            "booleanValue",
                        )
                        if key in field
                    ),
                    None,
                )
                row.append(value)

        rows.append(row)

    print("\n" + " | ".join(columns))
    print("-" * 70)

    for row in rows:
        print(" | ".join(
            str(value) if value is not None else "NULL"
            for value in row
        ))

    if response.get("NextToken"):
        print(
            "Hay mas resultados. Implementa paginacion si "
            "la consulta devuelve mas filas que el limite de la API."
        )

    return rows


def crear_tablas(data, secret_arn):
    """Crear las dos tablas relacionadas."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS clientes (
            cliente_id INTEGER NOT NULL,
            nombre VARCHAR(100),
            ciudad VARCHAR(100),
            PRIMARY KEY (cliente_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ventas (
            venta_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            producto VARCHAR(100),
            importe DECIMAL(12, 2),
            fecha DATE,
            PRIMARY KEY (venta_id)
        )
        """,
    ]

    for sql in statements:
        ejecutar_sql(data, secret_arn, sql)


def cargar_datos(data, secret_arn):
    """Vaciar las tablas y volver a cargar los CSV desde S3."""
    # Permite volver a ejecutar el programa sin duplicar registros.
    for table in ("ventas", "clientes"):
        ejecutar_sql(
            data,
            secret_arn,
            f"TRUNCATE TABLE {table}",
        )

    for table, filename in (
        ("clientes", "clientes.csv"),
        ("ventas", "ventas.csv"),
    ):
        sql = f"""
        COPY {table}
        FROM 's3://{BUCKET}/{DATA_PREFIX}{filename}'
        IAM_ROLE '{ROLE_ARN}'
        FORMAT AS CSV
        IGNOREHEADER 1
        """

        ejecutar_sql(data, secret_arn, sql)
        print(f"Datos cargados en {table}")


def ejecutar_consultas(data, secret_arn):
    """Ejecutar filtro, union y agregaciones."""
    queries = {
        "Ventas superiores a 900000": """
            SELECT venta_id, producto, importe, fecha
            FROM ventas
            WHERE importe > 900000
            ORDER BY importe DESC
        """,
        "Ventas relacionadas con clientes": """
            SELECT
                v.venta_id,
                c.nombre,
                c.ciudad,
                v.producto,
                v.importe,
                v.fecha
            FROM ventas v
            JOIN clientes c
                ON v.cliente_id = c.cliente_id
            ORDER BY v.venta_id
        """,
        "Resumen por cliente": """
            SELECT
                c.cliente_id,
                c.nombre,
                c.ciudad,
                COALESCE(SUM(v.importe), 0) AS total_vendido,
                COUNT(v.venta_id) AS cantidad_compras
            FROM clientes c
            LEFT JOIN ventas v
                ON c.cliente_id = v.cliente_id
            GROUP BY c.cliente_id, c.nombre, c.ciudad
            ORDER BY total_vendido DESC
        """,
        "Resumen por ciudad": """
            SELECT
                c.ciudad,
                SUM(v.importe) AS total_vendido,
                COUNT(v.venta_id) AS cantidad_ventas
            FROM clientes c
            JOIN ventas v
                ON c.cliente_id = v.cliente_id
            GROUP BY c.ciudad
            ORDER BY total_vendido DESC
        """,
        "Verificacion de registros": """
            SELECT 'clientes' AS tabla, COUNT(*) AS registros
            FROM clientes
            UNION ALL
            SELECT 'ventas', COUNT(*) FROM ventas
        """,
    }

    for title, sql in queries.items():
        print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
        ejecutar_sql(
            data,
            secret_arn,
            sql,
            recuperar=True,
        )


def main():
    print("=== 1. Preparar archivos en S3 ===")
    preparar_s3()

    print("\n=== 2. Verificar recursos y secreto ===")
    data, secret_arn = obtener_clientes_aws()

    print("\n=== 3. Crear tablas ===")
    crear_tablas(data, secret_arn)

    print("\n=== 4. Cargar archivos CSV ===")
    cargar_datos(data, secret_arn)

    print("\n=== 5. Ejecutar consultas y recuperar resultados ===")
    ejecutar_consultas(data, secret_arn)

    print("\nProceso finalizado correctamente.")


if __name__ == "__main__":
    main()

