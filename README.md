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

### Políticas IAM

En `Punto1/` se encuentran los siguientes archivos:

- `read_secret_key_policy.json`
- `write_and_delete_global_policy_secret_manager.json`

Estos archivos contienen las políticas de referencia utilizadas para los permisos de Secrets Manager.

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

Desde la raíz del repositorio, revisar los scripts disponibles:

```bash
ls -l Punto2/aws_cli/
```

Crear los recursos:

```bash
bash Punto2/aws_cli/cli_create.sh
```

Eliminar los recursos al finalizar las pruebas:

```bash
bash Punto2/aws_cli/cli_destroy.sh
```

Revisar el contenido de los scripts antes de ejecutarlos y confirmar los nombres de los recursos y la región configurada. Verificar en AWS que los recursos se hayan creado o eliminado correctamente.

### 2.2 Boto3

Instalar la biblioteca:

```bash
python -m pip install boto3
```

Boto3 utiliza la cadena estándar de credenciales de AWS. Si se utiliza el perfil `user_cli`, configurarlo en la terminal:

```bash
export AWS_PROFILE=user_cli
```

Revisar los scripts disponibles:

```bash
ls -l Punto2/boto3/
```

Crear los recursos:

```bash
python Punto2/boto3/boto3_create.py
```

Eliminar los recursos al finalizar:

```bash
python Punto2/boto3/boto3_destroy.py
```

Verificar que los scripts utilicen la región y las credenciales esperadas, y que eliminen únicamente los recursos creados para esta práctica.

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

### Políticas IAM

En `Punto2/` se encuentran:

- `UserCLI-EC2ACCESS-policy.json`
- `UserCLI-RDSACCESS-policy.json`
- `UserCLI-S3ACCESS-policy.json`
- `UserCLI-SecretsAndIdentity-policy.json`

Estas políticas corresponden a los permisos de acceso utilizados para los servicios del ejercicio.

En el repositorio se incluyen `Punto2/terraform/main.tf` y `Punto2/terraform/.terraform.lock.hcl`. El directorio `.terraform/` y los archivos `terraform.tfstate*` se excluyen mediante `.gitignore`, ya que corresponden a archivos locales y de estado de Terraform.

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

### Política IAM

En `Punto3/` se encuentra:

- `UserCLI-documentdb-policy.json`

---

## Punto 4. Amazon Neptune Serverless y consultas sobre grafos

### Objetivo

Desplegar un clúster de Amazon Neptune Serverless en AWS, construir un grafo que represente personas, vehículos y lugares, y ejecutar consultas utilizando el lenguaje de recorridos Gremlin.

La práctica incluye la configuración de red y permisos IAM, la conexión desde Python mediante HTTPS, la creación de vértices y relaciones, la ejecución de consultas y la eliminación de los recursos al finalizar.

### 4.1 Preparación de AWS

Seleccionar la región `us-east-2` (Ohio) y verificar la identidad utilizada por AWS CLI:

```bash
aws sts get-caller-identity
```

Consultar la región configurada:

```bash
aws configure get region
```

La infraestructura utilizada en la práctica incluye:

- Amazon Neptune Serverless.
- Una VPC y subredes de AWS.
- Un grupo de subredes para Neptune.
- Un Security Group para controlar el acceso al puerto TCP `8182`.
- Políticas IAM para administrar los recursos y autorizar las consultas de datos.
- Un endpoint público de Neptune para conectarse desde el equipo local.

El Security Group debe permitir el acceso al puerto `8182` únicamente desde la IP pública autorizada. No se debe habilitar el acceso indiscriminado desde Internet.

### 4.2 Crear y configurar Neptune Serverless

Desde la consola de AWS, ingresar a Amazon Neptune y crear un clúster con una configuración Serverless de bajo costo.

La configuración utilizada en esta práctica fue:

| Parámetro | Valor |
|---|---|
| Región | `us-east-2` |
| Clúster | `taller-neptune` |
| Instancia | `taller-neptune-instance` |
| Motor | Amazon Neptune |
| Clase | `db.serverless` |
| Capacidad mínima | 1 NCU |
| Capacidad máxima | 2 NCU |
| Autenticación IAM para datos | Habilitada |
| Puerto | `8182` |
| Retención de respaldos | 1 día |

Los valores corresponden a la configuración de referencia del ejercicio. Para reproducirlo en otra cuenta, verificar las opciones disponibles y los costos vigentes en la región seleccionada.

Crear o seleccionar un grupo de subredes que incluya las subredes necesarias para Neptune y asociar el Security Group correspondiente.

Una vez creado el clúster, consultar su estado:

```bash
aws neptune describe-db-clusters \
  --region us-east-2 \
  --db-cluster-identifier taller-neptune
```

Consultar la instancia:

```bash
aws neptune describe-db-instances \
  --region us-east-2 \
  --db-instance-identifier taller-neptune-instance
```

Esperar hasta que los recursos estén disponibles antes de continuar.

### 4.3 Configurar permisos IAM

En `Punto4/` se encuentran las políticas utilizadas como referencia:

- `neptune-data-access-policy.json`: permisos para acceder a los datos del grafo.
- `neptune-serverless-policy.json`: permisos para administrar los recursos de Neptune.

La identidad de AWS utilizada para ejecutar la práctica debe tener permisos suficientes para:

- Crear, consultar y eliminar los recursos de Neptune.
- Consultar el estado del motor.
- Ejecutar operaciones de lectura, escritura y eliminación de datos mediante Gremlin.

Las políticas de administración de infraestructura y de acceso a los datos deben distinguirse. Para la autenticación IAM de las consultas se utilizan permisos de Neptune Data API, como `neptune-db:ReadDataViaQuery`, `neptune-db:WriteDataViaQuery` y `neptune-db:DeleteDataViaQuery`, según las operaciones que se requieran.

Los permisos deben limitarse a los recursos del ejercicio y no deben conceder privilegios administrativos innecesarios.

### 4.4 Instalar las dependencias de Python

Desde la raíz del repositorio, instalar las bibliotecas requeridas:

```bash
python -m pip install boto3 requests requests-aws4auth
```

Verificar que AWS CLI tenga credenciales válidas y que la identidad utilizada disponga de los permisos correspondientes:

```bash
aws sts get-caller-identity
```

Si se utiliza un perfil diferente al predeterminado, configurar `AWS_PROFILE` antes de ejecutar los scripts:

```bash
export AWS_PROFILE=<NOMBRE_DEL_PERFIL>
```

No almacenar claves de acceso, tokens ni contraseñas directamente en el código fuente.

### 4.5 Configurar y comprobar la conexión

El archivo `Punto4/test_connection.py` permite comprobar la conexión con Neptune.

Obtener el endpoint de la instancia creada:

```bash
aws neptune describe-db-instances \
  --region us-east-2 \
  --db-instance-identifier taller-neptune-instance \
  --query "DBInstances[0].Endpoint.Address" \
  --output text
```

El endpoint obtenido debe utilizarse en los scripts Python, junto con el puerto `8182`.

Comprobar el estado del motor:

```bash
aws neptunedata get-engine-status \
  --region us-east-2 \
  --endpoint-url https://<ENDPOINT_NEPTUNE>:8182
```

Reemplazar `<ENDPOINT_NEPTUNE>` por el endpoint real de la instancia.

Ejecutar la prueba de conexión desde la raíz del repositorio:

```bash
python Punto4/test_connection.py
```

La conexión implementada utiliza HTTPS y firma de solicitudes mediante AWS Signature Version 4 (SigV4), con el servicio de firma `neptune-db`. La autenticación de red se complementa con las reglas del Security Group.

La arquitectura de acceso se realiza directamente desde el equipo local al endpoint público de Neptune; no utiliza una instancia EC2 ni un túnel SSH.

### 4.6 Construir el grafo

El archivo `Punto4/grafo_neptune.py` crea los vértices y las relaciones del modelo de transporte.

Ejecutar desde la raíz del repositorio:

```bash
python Punto4/grafo_neptune.py
```

El grafo contiene 10 vértices distribuidos en tres categorías:

- **Personas:** Ana, Luis, Marta y Juan.
- **Vehículos:** Bus1, Bus2 y Van1.
- **Lugares:** Universidad, Estacion y Centro.

También contiene 15 relaciones dirigidas:

| Relación | Significado |
|---|---|
| `VIAJA_EN` | Una persona utiliza un vehículo. |
| `DESTINO` | Una persona tiene un lugar como destino. |
| `CONECTA` | Un vehículo conecta con un lugar. |
| `CONDUCE` | Una persona conduce un vehículo. |

El script limpia los vértices existentes antes de insertar el grafo de prueba. Por tanto, debe ejecutarse únicamente sobre el clúster destinado a esta práctica, ya que puede eliminar los datos que ya existan en él.

Al terminar, comprobar que la salida confirme la creación de los vértices y las relaciones esperadas.

### 4.7 Ejecutar las consultas Gremlin

El archivo `Punto4/consultas_neptune.py` ejecuta cuatro consultas sobre el grafo creado.

Ejecutar:

```bash
python Punto4/consultas_neptune.py
```

Las consultas permiten:

1. Consultar las personas y los vehículos que utilizan.
2. Consultar las personas y sus destinos.
3. Consultar los vehículos y los lugares que conectan.
4. Recorrer varias relaciones para identificar lugares conectados a los vehículos utilizados por las personas.

Revisar la salida de cada consulta y guardar capturas de los resultados para documentar la ejecución.

### 4.8 Modelo del grafo y arquitectura de acceso

Los diagramas exportados se encuentran en el directorio `Punto4/`:

- `Punto4/grafo_neptune_transporte.png`: representación de las personas, los vehículos, los lugares y sus relaciones.
- `Punto4/arquitectura_acceso_neptune.png`: arquitectura de conexión desde el equipo local hasta Amazon Neptune Serverless.

El modelo del grafo representa las entidades y relaciones del sistema de transporte. La arquitectura muestra el equipo local, la conexión HTTPS, la VPC, el Security Group y Amazon Neptune Serverless.

### 4.9 Eliminar los recursos de Neptune

Después de guardar el código, los resultados y las evidencias, eliminar los recursos para evitar cargos posteriores.

Primero, solicitar la eliminación de la instancia:

```bash
aws neptune delete-db-instance \
  --region us-east-2 \
  --db-instance-identifier taller-neptune-instance \
  --no-skip-final-snapshot
```

Si AWS solicita un identificador para la instantánea final, utilizar uno único. La creación de la instantánea puede generar costos de almacenamiento.

Consultar el estado de la instancia:

```bash
aws neptune describe-db-instances \
  --region us-east-2 \
  --db-instance-identifier taller-neptune-instance
```

Esperar hasta que la instancia haya desaparecido. Si se eligió conservar la instantánea final, esta no se elimina automáticamente con la instancia.

Después, eliminar el clúster:

```bash
aws neptune delete-db-cluster \
  --region us-east-2 \
  --db-cluster-identifier taller-neptune \
  --skip-final-snapshot
```

Verificar las opciones y el estado antes de ejecutar el comando.

Comprobar que el clúster ya no exista:

```bash
aws neptune describe-db-clusters \
  --region us-east-2 \
  --db-cluster-identifier taller-neptune
```

Cuando el clúster haya desaparecido, comprobar los recursos auxiliares y eliminar únicamente los creados para esta práctica, siempre que no tengan dependencias:

- Grupo de subredes `taller-neptune-subnets`.
- Security Group utilizado exclusivamente por Neptune.
- Políticas IAM creadas exclusivamente para el ejercicio.
- Instantánea final, si ya no se necesita conservar.

No eliminar la VPC predeterminada ni las subredes compartidas. Antes de eliminar un Security Group o una política IAM, comprobar que ningún otro recurso o ejercicio los esté utilizando.

**Estado de limpieza de la ejecución realizada:** se eliminaron la instancia `taller-neptune-instance`, el clúster `taller-neptune`, el Security Group `taller-neptune-sg` y el grupo de subredes `taller-neptune-subnets`. Las consultas de verificación no mostraron instancias, clústeres ni instantáneas manuales de Neptune en la región `us-east-2`.

Esta comprobación corresponde a la ejecución realizada y no garantiza que futuras ejecuciones hayan eliminado todos los recursos. Antes de repetir la práctica, verificar el estado de los recursos existentes.

### 4.10 Evidencias de ejecución

Para documentar el resultado del ejercicio, conservar:

- Captura de la configuración y estado del clúster Serverless.
- Resultado de la comprobación del motor.
- Salida de la creación del grafo con los 10 vértices y las 15 relaciones.
- Resultados de las cuatro consultas Gremlin.
- Diagrama del modelo del grafo.
- Diagrama de arquitectura de acceso.
- Evidencia de la eliminación de la instancia y del clúster.

Las capturas no deben mostrar credenciales ni información sensible.

---

## Punto 5. Amazon Redshift Serverless con Boto3

### Objetivo

Implementar un flujo de procesamiento de datos en Amazon Redshift Serverless utilizando Python y Boto3. La solución carga archivos CSV en Amazon S3, crea las tablas de destino, importa los datos mediante `COPY` y ejecuta consultas analíticas a través de Redshift Data API.

El ejercicio utiliza dos tablas relacionadas (`clientes` y `ventas`) para analizar las transacciones por importe, cliente y ciudad.

### Estructura del proyecto

```text
Punto5/
├── datos/
│   ├── clientes.csv
│   └── ventas.csv
├── python/
│   └── ejecutar_redshift.py
├── sql/
│   ├── consultas.sql
│   └── crear_tablas.sql
├── redshift-s3-read.json
├── redshift-s3-trust.json
└── redshift_policy.json
```

Descripción de los archivos:

- `datos/clientes.csv`: información de los clientes, incluyendo identificador, nombre y ciudad.
- `datos/ventas.csv`: transacciones con identificador de venta, cliente, producto, importe y fecha.
- `python/ejecutar_redshift.py`: programa principal que automatiza la preparación de S3, la validación de recursos, la creación de tablas, la carga de datos y la ejecución de consultas.
- `sql/crear_tablas.sql`: definición de las tablas `clientes` y `ventas`.
- `sql/consultas.sql`: consultas SQL utilizadas para el análisis de los datos.
- `redshift-s3-read.json`: política que permite a Redshift leer los archivos de S3.
- `redshift-s3-trust.json`: política de confianza que permite a Redshift asumir el rol IAM.
- `redshift_policy.json`: política de referencia para los permisos de administración y ejecución de la práctica.

### 5.1. Requisitos previos

Se requiere:

- Una cuenta de AWS con permisos suficientes para utilizar S3, Secrets Manager, Redshift Serverless y Redshift Data API.
- AWS CLI configurado con credenciales válidas.
- Python 3 y Boto3.
- Un namespace y un workgroup de Redshift Serverless creados y disponibles.
- Un secreto en AWS Secrets Manager con las credenciales de acceso a Redshift.
- Un rol IAM asociado al namespace que permita a Redshift leer los archivos del bucket S3.

La configuración utilizada en el ejercicio es:

| Parámetro | Valor |
|---|---|
| Región | `us-east-2` (Ohio) |
| Namespace | `taller-redshift-ns` |
| Workgroup | `taller-redshift-wg` |
| Base de datos | `taller_dw` |
| Secreto | `taller/redshift/admin` |
| Rol IAM | `RedshiftS3ReadRole` |
| Bucket S3 | `talleraws-redshift-<ACCOUNT_ID>` |
| Prefijo de archivos | `datos/` |

Los recursos de infraestructura deben estar creados antes de ejecutar el programa. El script automatiza el flujo de datos, pero no crea el namespace ni el workgroup de Redshift Serverless.

### 5.2. Configurar las credenciales de AWS

Configurar o seleccionar un perfil de AWS con los permisos necesarios. Por ejemplo, si se utiliza el perfil `user_cli`:

```bash
export AWS_PROFILE=user_cli
```

Comprobar que las credenciales sean válidas:

```bash
aws sts get-caller-identity
```

El programa utiliza las credenciales del perfil configurado para realizar las llamadas a AWS. No se deben incluir claves de acceso ni contraseñas directamente en el código fuente.

### 5.3. Instalar las dependencias

Desde la raíz del repositorio, instalar Boto3:

```bash
python -m pip install boto3
```

Si se utiliza un entorno virtual o conda, activarlo antes de instalar la dependencia y ejecutar el programa.

### 5.4. Preparar y cargar los datos

Los archivos de entrada se encuentran en `Punto5/datos/`. El programa utiliza estos archivos para cargarlos en S3 y posteriormente importarlos en Redshift.

Desde la raíz del repositorio, ejecutar:

```bash
python Punto5/python/ejecutar_redshift.py
```

El programa realiza automáticamente las siguientes operaciones:

1. **Preparación de S3:** verifica si existe el bucket del ejercicio, lo crea si no existe y carga `clientes.csv` y `ventas.csv` en el prefijo `datos/`. También verifica la existencia de los archivos cargados.
2. **Validación de recursos:** comprueba el secreto de Secrets Manager y el estado del namespace y del workgroup de Redshift Serverless. También verifica la asociación del rol IAM utilizado para acceder a S3.
3. **Creación de tablas:** ejecuta las sentencias SQL para crear las tablas `clientes` y `ventas` si todavía no existen.
4. **Carga de datos:** limpia los datos anteriores de las tablas y ejecuta las sentencias `COPY` para importar los CSV desde S3 mediante el rol IAM.
5. **Ejecución de consultas:** envía las consultas a Redshift Data API, espera a que finalicen y recupera los resultados.
6. **Verificación:** consulta la cantidad de registros cargados para comprobar el resultado del proceso.

No es necesario ejecutar manualmente los archivos SQL ni copiar las sentencias en Query Editor v2 para reproducir el flujo.

**Importante:** el programa vacía las tablas antes de volver a cargar los datos. Cada ejecución reemplaza los registros anteriores por los datos presentes en los CSV locales. Ejecutarlo únicamente sobre la base de datos destinada a esta práctica.

### 5.5. Modelo de datos

El ejercicio utiliza dos tablas relacionadas por el campo `cliente_id`.

**Tabla `clientes`**

| Campo | Descripción |
|---|---|
| `cliente_id` | Identificador del cliente |
| `nombre` | Nombre del cliente |
| `ciudad` | Ciudad de residencia |

**Tabla `ventas`**

| Campo | Descripción |
|---|---|
| `venta_id` | Identificador de la venta |
| `cliente_id` | Cliente asociado a la transacción |
| `producto` | Producto vendido |
| `importe` | Valor de la venta en pesos colombianos |
| `fecha` | Fecha de la transacción |

La relación entre ambas tablas permite asociar cada venta con el cliente que la realizó y analizar los resultados por cliente o ciudad.

### 5.6. Consultas y preguntas de negocio

El programa ejecuta las consultas analíticas definidas para el ejercicio.

1. **Ventas superiores a $900.000 COP:** identifica las transacciones que superan el importe establecido mediante un filtro `WHERE`.
2. **Detalle de ventas y clientes:** utiliza `JOIN` para relacionar las transacciones con los nombres y ciudades de los clientes.
3. **Ventas por cliente:** utiliza `SUM`, `COUNT` y `GROUP BY` para calcular el importe acumulado y el número de compras de cada cliente.
4. **Ventas por ciudad:** agrupa las transacciones por ciudad para comparar los ingresos y la cantidad de ventas.

Estas consultas demuestran el uso de filtros, uniones y agregaciones para transformar los datos transaccionales en información útil para el análisis comercial.

### 5.7. Verificación de resultados

Al finalizar la ejecución, el programa debe mostrar los resultados de las consultas y los conteos de las tablas.

Con los archivos CSV del proyecto, se esperan los siguientes conteos:

| Tabla | Registros esperados |
|---|---:|
| `clientes` | 6 |
| `ventas` | 12 |

Si las cantidades no coinciden, revisar los mensajes de error del programa, el contenido de los CSV, la ubicación de los archivos en S3 y los permisos del rol IAM.

También se puede utilizar Query Editor v2 como herramienta opcional de inspección, siempre que la base de datos continúe disponible. No es necesario utilizarlo para ejecutar el procedimiento automatizado.

### 5.8. Limpieza de recursos

Al terminar las pruebas y guardar las evidencias, eliminar los recursos exclusivos del ejercicio para reducir costos.

Los recursos que deben revisarse son:

- Workgroup de Redshift Serverless.
- Namespace de Redshift Serverless.
- Bucket S3 y los objetos almacenados.
- Secreto de Secrets Manager.
- Rol IAM y sus políticas específicas, siempre que no estén compartidos con otros ejercicios.

Antes de eliminar el namespace, verificar que el workgroup haya sido eliminado y que no queden recursos dependientes. Para eliminar el bucket, primero deben borrarse sus objetos.

No eliminar recursos compartidos, como una VPC predeterminada, ni políticas IAM utilizadas por otros puntos del taller.

### 5.9. Evidencias de ejecución

Para documentar el ejercicio, conservar capturas que demuestren:

- La carga de los dos archivos CSV a S3.
- La creación de las tablas y la carga de datos en Redshift.
- Los resultados de las cuatro consultas analíticas.
- La verificación de los seis clientes y las doce ventas.

Las capturas deben mostrar los resultados sin exponer contraseñas, claves de acceso ni valores sensibles de Secrets Manager.

### Conclusión

La práctica demuestra cómo automatizar un flujo de datos en AWS mediante Boto3, Amazon S3, Amazon Redshift Serverless y Redshift Data API. Los archivos CSV se almacenan en S3 y se importan a las tablas de Redshift mediante `COPY`, utilizando un rol IAM con permisos de lectura.

Posteriormente, el programa ejecuta consultas SQL para filtrar transacciones, relacionar clientes con ventas y calcular indicadores por cliente y ciudad. Este flujo integra almacenamiento, carga y análisis de datos, y permite reproducir el ejercicio sin ejecutar manualmente las consultas desde la consola de AWS.

---

## Punto 6. Implementación de AWS Glue Data Catalog y Amazon Athena

### 6.1. Objetivo

Implementar un proceso de consulta y análisis de ventas almacenadas en Amazon S3 utilizando AWS Glue Data Catalog y Amazon Athena.

El ejercicio permite:

- Almacenar un archivo CSV en Amazon S3.
- Descubrir automáticamente su esquema mediante un crawler de AWS Glue.
- Consultar y analizar los datos con SQL en Athena.
- Actualizar el conjunto de datos y comprobar que las consultas reflejen los cambios.
- Comparar una tabla creada automáticamente con otra creada manualmente.

### 6.2. Servicios utilizados

| Servicio | Función |
|---|---|
| Amazon S3 | Almacenar el archivo CSV y los resultados de Athena. |
| AWS Glue Data Catalog | Mantener los metadatos y el esquema de la tabla. |
| AWS Glue Crawler | Detectar el esquema del archivo almacenado en S3. |
| Amazon Athena | Ejecutar consultas SQL directamente sobre los datos en S3. |
| AWS IAM | Controlar los permisos de acceso entre los servicios. |

### 6.3. Estructura local

Los archivos del punto están organizados de la siguiente manera:

```text
Punto6/
├── datos/
│   ├── ventas.csv
│   └── ventas_inicial.csv
└── Glue-Athena-policy.json
```

- `datos/ventas.csv`: conjunto actualizado con 28 registros.
- `datos/ventas_inicial.csv`: conjunto original con 24 registros.
- `Glue-Athena-policy.json`: archivo de política IAM utilizada como referencia para los permisos de Glue.

Los comandos siguientes se ejecutan desde la carpeta `Punto6/`, salvo que se indique lo contrario.

### 6.4. Requisitos previos

- Una cuenta de AWS con permisos para administrar S3, IAM, Glue y Athena.
- AWS CLI configurado con credenciales válidas.
- Región `us-east-2` (Ohio).
- Un bucket S3 disponible. Para este ejercicio se utilizó `jddh-0717-de`.

Verificar la identidad y la región:

```bash
aws sts get-caller-identity
aws configure get region
```

Definir variables para los comandos posteriores:

```bash
export AWS_REGION=us-east-2
export BUCKET=jddh-0717-de
export DATABASE=taller_aws_punto6
export CRAWLER=crawler_ventas_punto6
```

En Fish, las variables equivalentes se pueden definir así:

```fish
set -x AWS_REGION us-east-2
set -x BUCKET jddh-0717-de
set -x DATABASE taller_aws_punto6
set -x CRAWLER crawler_ventas_punto6
```

### 6.5. Preparar y cargar los datos en S3

El archivo CSV contiene las columnas:

```text
id_venta,fecha,ciudad,categoria,monto
```

El conjunto inicial contiene 24 ventas. Posteriormente se agregaron cuatro registros, para completar 28 ventas.

Comprobar los archivos locales:

```bash
head -n 5 datos/ventas.csv
```

Contar los registros, sin incluir el encabezado:

```bash
awk 'END {print NR-1}' datos/ventas_inicial.csv
awk 'END {print NR-1}' datos/ventas.csv
```

Los resultados esperados son `24` y `28`, respectivamente.

Crear el prefijo lógico y cargar el archivo actualizado:

```bash
aws s3 cp datos/ventas.csv \
  s3://jddh-0717-de/punto6/ventas.csv \
  --region us-east-2
```

Verificar la carga:

```bash
aws s3 ls s3://jddh-0717-de/punto6/ --region us-east-2
```

**Nota:** S3 no requiere crear explícitamente una carpeta. El prefijo `punto6/` aparece al cargar el objeto.

### 6.6. Configurar permisos de AWS Glue

Se utilizó el rol IAM `AWSGlueServiceRole`, con la política administrada `AWSGlueServiceRole` y permisos adicionales para leer los datos del prefijo `punto6/` del bucket.

La política de acceso a S3 debe permitir, como mínimo:

- `s3:ListBucket` sobre el bucket, limitado al prefijo del ejercicio cuando corresponda.
- `s3:GetBucketLocation` sobre el bucket.
- `s3:GetObject` sobre `arn:aws:s3:::jddh-0717-de/punto6/*`.

La relación de confianza del rol debe permitir que el servicio `glue.amazonaws.com` asuma el rol mediante `sts:AssumeRole`.

La identidad que ejecuta los comandos también necesita permisos para crear y administrar los recursos de Glue. Si crea o modifica el rol desde la CLI, necesitará los permisos IAM correspondientes; para pasar el rol a Glue, necesita `iam:PassRole`.

No se deben guardar claves de acceso ni contraseñas en el repositorio.

### 6.7. Crear la base de datos de Glue

Crear la base de datos del catálogo:

```bash
aws glue create-database \
  --database-input '{"Name":"taller_aws_punto6","Description":"Catalogo de ventas del Punto 6"}' \
  --region us-east-2
```

Si la base de datos ya existe, no es necesario crearla nuevamente.

### 6.8. Crear y ejecutar el crawler

Crear el crawler para descubrir el esquema del CSV:

```bash
aws glue create-crawler \
  --name crawler_ventas_punto6 \
  --role arn:aws:iam::573992724610:role/AWSGlueServiceRole \
  --database-name taller_aws_punto6 \
  --targets '{"S3Targets":[{"Path":"s3://jddh-0717-de/punto6/"}]}' \
  --schema-change-policy '{"UpdateBehavior":"UPDATE_IN_DATABASE","DeleteBehavior":"DEPRECATE_IN_DATABASE"}' \
  --region us-east-2
```

Si el rol tiene un nombre o ARN diferente en otra cuenta, se debe reemplazar por el ARN del rol válido.

Iniciar el crawler:

```bash
aws glue start-crawler \
  --name crawler_ventas_punto6 \
  --region us-east-2
```

Consultar su estado:

```bash
aws glue get-crawler \
  --name crawler_ventas_punto6 \
  --query 'Crawler.State' \
  --output text \
  --region us-east-2
```

Esperar a que termine y verificar que la última ejecución haya finalizado correctamente.

### 6.9. Verificar la tabla generada

Consultar las tablas del catálogo:

```bash
aws glue get-tables \
  --database-name taller_aws_punto6 \
  --query 'TableList[].Name' \
  --output table \
  --region us-east-2
```

El crawler generó una tabla denominada `punto6`, con el siguiente esquema:

| Columna | Tipo |
|---|---|
| `id_venta` | `bigint` |
| `fecha` | `string` |
| `ciudad` | `string` |
| `categoria` | `string` |
| `monto` | `bigint` |

### 6.10. Configurar Amazon Athena

En la consola de AWS:

1. Abrir Amazon Athena en la región `us-east-2`.
2. Seleccionar la base de datos `taller_aws_punto6`.
3. Configurar una ubicación de resultados de consulta, por ejemplo:

```text
s3://jddh-0717-de/athena-results/punto6/
```

4. Ejecutar las consultas sobre la tabla `punto6`.

La ubicación de resultados debe existir como prefijo utilizable en S3 y Athena debe tener permisos para escribir en ella. Si la carpeta no existe, Athena puede crear los objetos bajo ese prefijo al ejecutar las consultas.

### 6.11. Consultas iniciales

**Consulta 1. Ventas de Medellín**

```sql
SELECT id_venta, fecha, ciudad, categoria, monto
FROM punto6
WHERE ciudad = 'Medellin'
ORDER BY monto DESC;
```

Con el conjunto inicial se obtuvieron nueve registros de Medellín.

**Consulta 2. Resumen de ventas por categoría en Medellín**

```sql
SELECT
    categoria,
    COUNT(*) AS cantidad_ventas,
    SUM(monto) AS total_ventas,
    AVG(monto) AS promedio_venta
FROM punto6
WHERE ciudad = 'Medellin'
GROUP BY categoria
ORDER BY total_ventas DESC;
```

Resultados esperados con los 24 registros iniciales:

| Categoría | Ventas | Total |
|---|---:|---:|
| Electronica | 4 | 5.040.000 |
| Hogar | 2 | 425.000 |
| Ropa | 3 | 325.000 |
| **Total** | **9** | **5.790.000** |

Los valores monetarios del ejercicio están expresados en pesos colombianos (COP).

### 6.12. Actualizar el conjunto de datos

El archivo `datos/ventas.csv` incluye cuatro registros adicionales:

```csv
25,2026-10-13,Medellin,Electronica,500000
26,2026-10-13,Bogota,Hogar,200000
27,2026-10-14,Cali,Ropa,175000
28,2026-10-14,Medellin,Hogar,300000
```

Para reproducir la actualización desde el conjunto inicial, primero se debe copiar `datos/ventas_inicial.csv` sobre `datos/ventas.csv` y luego añadir las cuatro filas anteriores. Si el archivo actualizado ya contiene 28 registros, no se deben añadir otra vez.

Volver a cargar el CSV en S3:

```bash
aws s3 cp datos/ventas.csv \
  s3://jddh-0717-de/punto6/ventas.csv \
  --region us-east-2
```

Ejecutar nuevamente el crawler para actualizar el catálogo:

```bash
aws glue start-crawler \
  --name crawler_ventas_punto6 \
  --region us-east-2
```

Esperar a que termine correctamente antes de consultar los datos.

### 6.13. Validar los datos actualizados

Volver a ejecutar la consulta de ventas de Medellín y la consulta de agregación por categoría.

Resultados esperados para Medellín:

| Categoría | Ventas | Total |
|---|---:|---:|
| Electronica | 5 | 5.540.000 |
| Hogar | 3 | 725.000 |
| Ropa | 3 | 325.000 |
| **Total** | **11** | **6.590.000** |

Comprobar también el total general:

```sql
SELECT
    COUNT(*) AS cantidad_ventas,
    SUM(monto) AS total_ventas
FROM punto6;
```

Resultado esperado:

| Registros | Total |
|---:|---:|
| 28 | 15.045.000 |

### 6.14. Crear una tabla manual en Athena

Como comparación, se creó la tabla `ventas_manual` sin utilizar un crawler:

```sql
CREATE EXTERNAL TABLE ventas_manual (
    id_venta BIGINT,
    fecha STRING,
    ciudad STRING,
    categoria STRING,
    monto BIGINT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'skip.header.line.count' = '1'
)
STORED AS TEXTFILE
LOCATION 's3://jddh-0717-de/punto6/';
```

Comparar ambas tablas:

```sql
SELECT 'punto6' AS tabla, COUNT(*) AS registros, SUM(monto) AS total
FROM punto6

UNION ALL

SELECT 'ventas_manual' AS tabla, COUNT(*) AS registros, SUM(monto) AS total
FROM ventas_manual;
```

Las dos tablas deben devolver 28 registros y un total de 15.045.000, siempre que ambas lean el mismo archivo actualizado.

### 6.15. Resultados y conclusiones

- AWS Glue identificó el esquema del CSV y registró la tabla en Data Catalog.
- Athena permitió consultar los datos de S3 con SQL, sin cargar las ventas en una base de datos tradicional.
- Al añadir cuatro ventas y volver a ejecutar el crawler, las consultas reflejaron los nuevos registros.
- La tabla creada manualmente produjo los mismos resultados que la tabla generada por Glue.
- Glue Data Catalog almacena metadatos; los registros continúan almacenados en S3.

### 6.16. Limpieza de recursos

Para evitar cargos innecesarios, se eliminaron los recursos creados para el ejercicio.

Si se desea repetir la limpieza desde la CLI, eliminar primero el crawler:

```bash
aws glue delete-crawler \
  --name crawler_ventas_punto6 \
  --region us-east-2
```

Eliminar las tablas del catálogo:

```bash
aws glue delete-table \
  --database-name taller_aws_punto6 \
  --name punto6 \
  --region us-east-2

aws glue delete-table \
  --database-name taller_aws_punto6 \
  --name ventas_manual \
  --region us-east-2
```

Eliminar la base de datos:

```bash
aws glue delete-database \
  --name taller_aws_punto6 \
  --region us-east-2
```

Los comandos anteriores fallarán si los recursos ya fueron eliminados; en ese caso, no es necesario repetirlos.

**Importante:** durante la limpieza de este taller se eliminaron todos los objetos del bucket `jddh-0717-de`, no solamente los del Punto 6. El bucket se conservó, pero quedó vacío. Para reproducir este punto, se deben volver a cargar el CSV y los resultados de Athena se generarán nuevamente al ejecutar las consultas.

No se recomienda borrar todo el contenido del bucket si contiene objetos pertenecientes a otros puntos del taller.

### 6.17. Consideraciones de costos y seguridad

- S3 puede generar cargos por almacenamiento y solicitudes.
- Athena cobra por la cantidad de datos procesados por las consultas.
- Glue puede generar cargos por las ejecuciones del crawler y otros recursos utilizados.
- Se deben limitar los permisos IAM al bucket y prefijo necesarios.
- Los resultados de Athena pueden contener datos consultados; deben almacenarse en una ubicación con acceso controlado.
- Antes de finalizar, verificar que no queden recursos innecesarios ni objetos de resultados que generen costos.



---

## Buenas prácticas para publicar el proyecto

Antes de subir los cambios al repositorio:

- No incluir contraseñas, claves de acceso AWS ni archivos `.pem`.
- No incluir `.env`, estados de Terraform ni el directorio `.terraform/`.
- Conservar los archivos de código, scripts, documentación y políticas IAM de ejemplo sin secretos.
- Revisar los cambios con `git status` y `git diff --cached`.
- Verificar en AWS que los recursos temporales hayan sido eliminados.
- Revisar Billing o Cost Explorer después de las pruebas, ya que los costos pueden tardar en actualizarse.