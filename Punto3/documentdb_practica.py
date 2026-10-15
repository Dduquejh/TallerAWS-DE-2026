
import json
import os

import boto3
from pymongo import MongoClient
from pymongo.server_api import ServerApi

REGION = "us-east-2"
SECRET_NAME = "docdb-practica-credentials"
ENDPOINT = (
    "docdb-practica.cluster-c1aymgwc63hv."
    "us-east-2.docdb.amazonaws.com"
)
CA_FILE = os.path.expanduser("~/.certs/docdb/global-bundle.pem")


def obtener_credenciales():
    session = boto3.session.Session(region_name=REGION)
    secrets = session.client("secretsmanager")

    response = secrets.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(response["SecretString"])

    # Ajusta estas claves si tu secreto usa otros nombres.
    username = secret.get("username") or secret.get("user")
    password = secret.get("password")

    if not username or not password:
        raise ValueError(
            "El secreto debe contener username y password. "
            "Revisa las claves JSON guardadas en Secrets Manager."
        )

    return username, password


def main():
    username, password = obtener_credenciales()

    # El túnel SSH debe estar abierto en otra terminal.
    uri = (
        f"mongodb://{username}:{password}@{ENDPOINT}:27017/"
        "?tls=true&authSource=admin&directConnection=true"
    )

    client = MongoClient(
        uri,
        tlsCAFile=CA_FILE,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        appName="TallerAWS-DocumentDB",
    )

    try:
        client.admin.command("ping")
        print("Conexión a DocumentDB: OK")

        db = client["practica_documentdb"]
        collection = db["ventas"]

        # Permite repetir la práctica sin duplicar los documentos.
        collection.delete_many({"lote": "taller-2026"})

        documentos = [
            {
                "lote": "taller-2026",
                "id_venta": i,
                "producto": producto,
                "categoria": categoria,
                "ciudad": ciudad,
                "cantidad": cantidad,
                "precio_unitario": precio,
            }
            for i, (producto, categoria, ciudad, cantidad, precio)
            in enumerate([
                ("Laptop", "Tecnologia", "Medellin", 1, 2800000),
                ("Mouse", "Accesorios", "Envigado", 2, 65000),
                ("Teclado", "Accesorios", "Medellin", 1, 120000),
                ("Monitor", "Tecnologia", "Bogota", 2, 850000),
                ("Audifonos", "Accesorios", "Cali", 3, 95000),
                ("Tablet", "Tecnologia", "Envigado", 1, 1200000),
                ("Webcam", "Accesorios", "Bogota", 2, 180000),
                ("Impresora", "Oficina", "Medellin", 1, 700000),
                ("Silla", "Oficina", "Cali", 2, 450000),
                ("Disco SSD", "Tecnologia", "Bogota", 2, 320000),
            ], start=1)
        ]

        collection.insert_many(documentos)
        print("Documentos insertados:", collection.count_documents(
            {"lote": "taller-2026"}
        ))

        # 1. Búsqueda con filtro
        print("\n1. Ventas de la categoria Tecnologia:")
        filtro = {
            "lote": "taller-2026",
            "categoria": "Tecnologia",
        }
        for doc in collection.find(
            filtro, {"_id": 0}
        ).sort("precio_unitario", -1):
            print(doc)

        # 2. Ordenación
        print("\n2. Productos ordenados por precio descendente:")
        for doc in collection.find(
            {"lote": "taller-2026"},
            {"_id": 0, "producto": 1, "precio_unitario": 1},
        ).sort("precio_unitario", -1):
            print(doc)

        # 3. Agregación: ingresos por categoría
        pipeline = [
            {"$match": {"lote": "taller-2026"}},
            {
                "$group": {
                    "_id": "$categoria",
                    "unidades": {"$sum": "$cantidad"},
                    "ingresos": {
                        "$sum": {
                            "$multiply": [
                                "$cantidad",
                                "$precio_unitario",
                            ]
                        }
                    },
                }
            },
            {"$sort": {"ingresos": -1}},
        ]

        print("\n3. Agregación de ingresos por categoría:")
        for resultado in collection.aggregate(pipeline):
            print(resultado)

    finally:
        client.close()


if __name__ == "__main__":
    main()

