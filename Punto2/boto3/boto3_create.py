import boto3

REGION = "us-east-2"

BUCKET_NAME = "talleraws-de-2026-573992724610"
EC2_NAME = "TallerAWS-Boto3-EC2"
RDS_IDENTIFIER = "talleraws-boto3-rds"

AMI_ID = "ami-0ca656964bac97e7f"
INSTANCE_TYPE = "t3.micro"
SUBNET_ID = "subnet-096a4967a3ea16daa"
SECURITY_GROUP_ID = "sg-01cd7b4a43ef5a50c"
DB_SUBNET_GROUP = "default-vpc-0f97d7e96864377f2"


s3 = boto3.client("s3", region_name=REGION)
ec2 = boto3.client("ec2", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)


# ---------------------------------------------------------
# S3
# ---------------------------------------------------------

print("=== Creando S3 ===")

s3.create_bucket(
    Bucket=BUCKET_NAME,
    CreateBucketConfiguration={
        "LocationConstraint": REGION
    }
)

print(f"S3 creado: {BUCKET_NAME}")


# ---------------------------------------------------------
# EC2
# ---------------------------------------------------------

print("\n=== Creando EC2 ===")

response = ec2.run_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    MinCount=1,
    MaxCount=1,

    NetworkInterfaces=[
        {
            "DeviceIndex": 0,
            "AssociatePublicIpAddress": True,
            "SubnetId": SUBNET_ID,
            "Groups": [SECURITY_GROUP_ID]
        }
    ],

    TagSpecifications=[
        {
            "ResourceType": "instance",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "TallerAWS-Boto3-EC2"
                }
            ]
        }
    ]
)

instance_id = response["Instances"][0]["InstanceId"]

print(f"EC2 creada: {instance_id}")
print("Esperando a que EC2 esté disponible...")

ec2.get_waiter("instance_running").wait(
    InstanceIds=[instance_id]
)

print("EC2 está en estado running.")


# ---------------------------------------------------------
# RDS
# ---------------------------------------------------------

print("\n=== Creando RDS ===")

rds.create_db_instance(
    DBInstanceIdentifier=RDS_IDENTIFIER,
    Engine="postgres",
    DBInstanceClass="db.t3.micro",
    AllocatedStorage=20,
    StorageType="gp2",
    DBName="talleraws",
    MasterUsername="dbuser",
    ManageMasterUserPassword=True,
    DBSubnetGroupName=DB_SUBNET_GROUP,
    VpcSecurityGroupIds=[SECURITY_GROUP_ID],
    PubliclyAccessible=False,
    BackupRetentionPeriod=0,
    Tags=[
        {
            "Key": "Name",
            "Value": "TallerAWS-Boto3-RDS"
        }
    ]
)

print(f"RDS creado: {RDS_IDENTIFIER}")
print("Esperando a que RDS esté disponible...")

rds.get_waiter("db_instance_available").wait(
    DBInstanceIdentifier=RDS_IDENTIFIER
)

print("RDS está disponible.")


print("\n=== DESPLIEGUE COMPLETADO ===")
print(f"S3 : {BUCKET_NAME}")
print(f"EC2: {instance_id}")
print(f"RDS: {RDS_IDENTIFIER}")