# Taller AWS — Ingeniería de Datos

Guía de instalación, ejecución y limpieza de los recursos utilizados en el taller de AWS.

## Requisitos generales

- Cuenta de AWS con permisos IAM para los servicios utilizados.
- AWS CLI configurado con un usuario o rol IAM.
- Python 3 y `pip`.
- Terraform para el punto 2.
- Región de AWS: `us-east-2` (Ohio).

Verificar las herramientas instaladas:

```bash
aws --version
python --version
terraform version
```

Verificar la identidad de AWS:

```bash
aws sts get-caller-identity
```

Se recomienda utilizar un usuario o rol IAM con permisos mínimos necesarios, en lugar de credenciales de root.

> **Advertencia de costos:** los recursos de AWS pueden generar cargos mientras están activos. Revisa los recursos antes de crearlos y elimínalos al finalizar las pruebas.

---

## Punto 1. AWS Secrets Manager

### Objetivo

Crear y administrar un secreto en AWS Secrets Manager y consultar sus metadatos o valor utilizando AWS CLI y Python, según la implementación del punto.

### Procedimiento

1. Ingresar a la consola de AWS y seleccionar la región `us-east-2`.
2. Abrir **Secrets Manager**.
3. Crear el secreto con los campos y el formato solicitados por la actividad.
4. Configurar los permisos IAM para permitir el acceso al secreto.
5. Ejecutar el script Python correspondiente desde la raíz del repositorio.

```bash
python Punto1/punto1.py
```

Si el nombre del archivo es diferente, utilizar el script disponible en `Punto1/`.

### Verificar el secreto con AWS CLI

Consultar sus metadatos:

```bash
aws secretsmanager describe-secret \
  --secret-id "<NOMBRE_O_ARN_DEL_SECRETO>" \
  --region us-east-2
```

Consultar el valor del secreto:

```bash
aws secretsmanager get-secret-value \
  --secret-id "<NOMBRE_O_ARN_DEL_SECRETO>" \
  --region us-east-2
```

Reemplazar el marcador por el nombre o ARN del secreto creado.

**Seguridad:** la salida de `get-secret-value` puede contener contraseñas u otros datos sensibles. No incluirla en capturas públicas ni subirla a Git.

### Limpieza

Eliminar el secreto únicamente cuando ya no se necesite:

```bash
aws secretsmanager delete-secret \
  --secret-id "<NOMBRE_O_ARN_DEL_SECRETO>" \
  --region us-east-2
```

Por defecto, AWS programa la eliminación con un período de recuperación. Si se requiere eliminarlo inmediatamente, se debe revisar cuidadosamente la opción `--force-delete-without-recovery`.

---

## Punto 2. Comparación entre AWS CLI, Boto3 y Terraform

### Objetivo

Crear, consultar y eliminar recursos de AWS utilizando tres mecanismos de automatización:

- AWS CLI.
- Boto3 (Python).
- Terraform.

Los recursos del ejercicio incluyen S3, EC2 y RDS, de acuerdo con la configuración implementada.

### 2.1 AWS CLI

Comprobar la identidad y región:

```bash
aws sts get-caller-identity
aws configure get region
```

Ubicar los scripts de creación y eliminación:

```bash
find Punto2 -maxdepth 3 -type f
```

Revisar el contenido de los scripts antes de ejecutarlos y confirmar los nombres de recursos y la región.

Si los archivos tienen los nombres `cli_create.sh` y `cli_destroy.sh`, ejecutarlos desde la raíz:

```bash
chmod +x Punto2/cli/cli_create.sh Punto2/cli/cli_destroy.sh
./Punto2/cli/cli_create.sh
```

Verificar en la consola de AWS que los recursos se hayan creado correctamente.

Al finalizar:

```bash
./Punto2/cli/cli_destroy.sh
```

### 2.2 Boto3

Instalar la biblioteca:

```bash
python -m pip install boto3
```

Boto3 utiliza la cadena estándar de credenciales de AWS. Si se utiliza un perfil específico, configurarlo en la terminal antes de ejecutar el script:

```bash
export AWS_PROFILE=user_cli
```

Listar los archivos disponibles:

```bash
find Punto2/boto3 -maxdepth 2 -type f
```

Ejecutar el script de creación correspondiente. Por ejemplo, si se llama `boto3_create.py`:

```bash
python Punto2/boto3/boto3_create.py
```

Después, ejecutar el script de eliminación correspondiente que se encuentre en esa carpeta.

Revisar siempre que los scripts eliminen únicamente los recursos creados para la práctica.

### 2.3 Terraform

Ingresar al directorio del proyecto:

```bash
cd Punto2/terraform
```

Inicializar Terraform:

```bash
terraform init
```

Validar la configuración:

```bash
terraform validate
```

Revisar el plan antes de crear recursos:

```bash
terraform plan
```

Crear los recursos:

```bash
terraform apply
```

Confirmar la operación después de revisar los cambios propuestos.

Para eliminar los recursos administrados por Terraform:

```bash
terraform destroy
```

Revisar el plan de destrucción antes de confirmarlo.

**Importante:** no eliminar manualmente recursos de red compartidos que no pertenezcan al ejercicio. Los archivos de estado de Terraform pueden contener información sensible, por lo que no deben publicarse en Git.

### Comparación de los métodos

- **AWS CLI:** permite ejecutar operaciones directamente desde la terminal.
- **Boto3:** permite automatizar operaciones desde programas Python y controlar el flujo de ejecución.
- **Terraform:** permite declarar la infraestructura como código y gestionar su ciclo de vida mediante un estado.

---

## Punto 3. Amazon DocumentDB y MongoDB Compass

### Objetivo

Desplegar Amazon DocumentDB con una configuración de bajo costo, conectarse de forma segura desde Python y MongoDB Compass, ejecutar operaciones CRUD y eliminar los recursos al terminar.

### 3.1 Preparación de AWS

Seleccionar la región `us-east-2` y preparar:

1. Un secreto en Secrets Manager con las credenciales de la base de datos.
2. Un clúster de Amazon DocumentDB y una instancia.
3. Un grupo de seguridad para DocumentDB que permita TCP `27017` desde el grupo de seguridad del EC2 utilizado como túnel.
4. Una instancia EC2 que pueda alcanzar DocumentDB por la red privada.
5. Una política IAM que permita al usuario o rol de ejecución leer el secreto.

El archivo `Punto3/UserCLI-documentdb-policy.json` contiene una política de ejemplo. Revisar el ARN del secreto y adaptar la política a los recursos creados.

No exponer el puerto `27017` a todo Internet ni guardar contraseñas o claves privadas en el repositorio.

### 3.2 Instalar dependencias

Desde la raíz del repositorio:

```bash
python -m pip install boto3 pymongo
```

Descargar el paquete de certificados CA de AWS:

```bash
mkdir -p ~/.certs/docdb
curl -o ~/.certs/docdb/global-bundle.pem \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

El certificado debe permanecer localmente en el equipo.

### 3.3 Ejecutar la práctica en Python

Revisar `Punto3/documentdb_practica.py` y actualizar, según la infraestructura recreada:

- Región.
- Nombre o ARN del secreto.
- Endpoint del clúster.
- Ruta del certificado CA.

Ejecutar:

```bash
python Punto3/documentdb_practica.py
```

El programa recupera las credenciales desde Secrets Manager y utiliza `pymongo` para conectarse mediante TLS y ejecutar las operaciones definidas en el código.

La identidad de AWS utilizada por el programa debe tener el permiso `secretsmanager:GetSecretValue` sobre el secreto.

### 3.4 Conexión desde MongoDB Compass

La base de datos se encuentra en una red privada. Para conectarse desde el equipo local se utiliza una instancia EC2 como túnel SSH.

Con la clave privada descargada y guardada localmente:

```bash
chmod 400 ~/.ssh/docdb-practica-key.pem
```

Abrir el túnel:

```bash
ssh -i ~/.ssh/docdb-practica-key.pem \
  -N -L 27017:<ENDPOINT_DOCUMENTDB>:27017 \
  ec2-user@<IP_PUBLICA_EC2>
```

Mantener esa terminal abierta mientras se utiliza Compass. Reemplazar los valores entre `< >` por los datos de la infraestructura recreada.

En MongoDB Compass configurar:

- **Hostname:** endpoint del clúster DocumentDB.
- **Port:** `27017`.
- **TLS/SSL:** habilitado.
- **CA certificate:** archivo `global-bundle.pem`.
- **Authentication:** usuario y contraseña del secreto.
- **Authentication Database:** `admin`.
- **Direct Connection:** activada si corresponde a la configuración utilizada.

El hostname debe coincidir con el certificado TLS. Si se utiliza una resolución local del endpoint hacia `127.0.0.1` para el túnel, conservar el hostname original en Compass para la validación del certificado.

### 3.5 Eliminar los recursos

Al finalizar las pruebas, eliminar los recursos en este orden:

1. Instancia de DocumentDB.
2. Clúster de DocumentDB, después de que la instancia haya desaparecido.
3. Instancia EC2 del túnel.
4. Secreto de Secrets Manager.
5. Grupos de seguridad creados exclusivamente para esta práctica.

Eliminar la instancia de DocumentDB:

```bash
aws docdb delete-db-instance \
  --db-instance-identifier docdb-practica-instance \
  --region us-east-2
```

Cuando la instancia ya no exista, eliminar el clúster:

```bash
aws docdb delete-db-cluster \
  --db-cluster-identifier docdb-practica \
  --skip-final-snapshot \
  --region us-east-2
```

Terminar el EC2, sustituyendo el ID por el real:

```bash
aws ec2 terminate-instances \
  --instance-ids <INSTANCE_ID_EC2> \
  --region us-east-2
```

Eliminar el secreto de la práctica de forma inmediata e irreversible, únicamente si ya no se necesita:

```bash
aws secretsmanager delete-secret \
  --secret-id docdb-practica-credentials \
  --force-delete-without-recovery \
  --region us-east-2
```

Eliminar los grupos de seguridad solo después de verificar sus identificadores y confirmar que no se utilizan en otros recursos. No eliminar la VPC ni las subredes compartidas.

---

## Buenas prácticas para publicar el proyecto

Antes de subir los cambios al repositorio:

- No incluir contraseñas, claves de acceso AWS ni archivos `.pem`.
- No incluir `.env`, estados de Terraform ni el directorio `.terraform/`.
- Conservar los archivos de código, scripts, documentación y políticas IAM de ejemplo sin secretos.
- Revisar los cambios con `git status` y `git diff --cached`.
- Verificar en AWS que los recursos temporales hayan sido eliminados.
- Revisar Billing o Cost Explorer después de las pruebas, ya que los costos pueden tardar en actualizarse.

