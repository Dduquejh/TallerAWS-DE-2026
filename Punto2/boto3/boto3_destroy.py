import boto3

REGION = "us-east-2"

BUCKET_NAME = "talleraws-de-2026-573992724610"
RDS_IDENTIFIER = "talleraws-boto3-rds"
EC2_NAME = "TallerAWS-Boto3-EC2"


s3 = boto3.client("s3", region_name=REGION)
ec2 = boto3.client("ec2", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)


# ---------------------------------------------------------
# Buscar EC2
# ---------------------------------------------------------

print("=== Buscando EC2 ===")

response = ec2.describe_instances(
    Filters=[
        {
            "Name": "tag:Name",
            "Values": [EC2_NAME]
        },
        {
            "Name": "instance-state-name",
            "Values": [
                "pending",
                "running",
                "stopping",
                "stopped"
            ]
        }
    ]
)

instance_ids = []

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        instance_ids.append(instance["InstanceId"])


# ---------------------------------------------------------
# Eliminar EC2
# ---------------------------------------------------------

if instance_ids:
    print(f"EC2 encontrada: {instance_ids}")

    ec2.terminate_instances(
        InstanceIds=instance_ids
    )

    print("Esperando a que EC2 termine...")

    ec2.get_waiter("instance_terminated").wait(
        InstanceIds=instance_ids
    )

    print("EC2 eliminada.")
else:
    print("No se encontró la EC2.")


# ---------------------------------------------------------
# Eliminar RDS
# ---------------------------------------------------------

print("\n=== Eliminando RDS ===")

try:
    rds.delete_db_instance(
        DBInstanceIdentifier=RDS_IDENTIFIER,
        SkipFinalSnapshot=True,
        DeleteAutomatedBackups=True
    )

    print("RDS eliminado. Esperando confirmación...")

    rds.get_waiter("db_instance_deleted").wait(
        DBInstanceIdentifier=RDS_IDENTIFIER
    )

    print("RDS eliminado completamente.")

except rds.exceptions.DBInstanceNotFoundFault:
    print("RDS no existe.")


# ---------------------------------------------------------
# Eliminar S3
# ---------------------------------------------------------

print("\n=== Eliminando S3 ===")

try:
    # El bucket debe estar vacío antes de eliminarlo.
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME
    )

    if "Contents" in response:
        objects = [
            {"Key": obj["Key"]}
            for obj in response["Contents"]
        ]

        s3.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={"Objects": objects}
        )

        print("Objetos eliminados del bucket.")

    s3.delete_bucket(
        Bucket=BUCKET_NAME
    )

    print("S3 eliminado.")

except s3.exceptions.NoSuchBucket:
    print("El bucket no existe.")


print("\n=== ELIMINACIÓN COMPLETADA ===")