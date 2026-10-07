#!/usr/bin/env bash

set -e

# =========================
# Configuración
# =========================

REGION="us-east-2"

BUCKET_NAME="talleraws-de-2026-573992724610-cli"

AMI_ID="ami-0ca656964bac97e7f"
INSTANCE_TYPE="t3.micro"
SUBNET_ID="subnet-096a4967a3ea16daa"
SECURITY_GROUP_ID="sg-01cd7b4a43ef5a50c"

RDS_IDENTIFIER="talleraws-cli-rds"
DB_NAME="talleraws"
DB_USERNAME="dbuser"
DB_SUBNET_GROUP="default-vpc-0f97d7e96864377f2"

# =========================
# S3
# =========================

echo "=== Creando S3 ==="

if aws s3api head-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" 2>/dev/null; then

    echo "El bucket ya existe: $BUCKET_NAME"

else

    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION"

    echo "S3 creado: $BUCKET_NAME"
fi


# =========================
# EC2
# =========================

echo
echo "=== Creando EC2 ==="

INSTANCE_ID=$(aws ec2 run-instances \
    --region "$REGION" \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --subnet-id "$SUBNET_ID" \
    --security-group-ids "$SECURITY_GROUP_ID" \
    --associate-public-ip-address \
    --tag-specifications \
        'ResourceType=instance,Tags=[{Key=Name,Value=TallerAWS-CLI-EC2}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "EC2 creado: $INSTANCE_ID"

echo "Esperando a que EC2 esté en estado running..."

aws ec2 wait instance-running \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID"

echo "EC2 listo."

PUBLIC_IP=$(aws ec2 describe-instances \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "IP pública: $PUBLIC_IP"


# =========================
# RDS
# =========================

echo
echo "=== Creando RDS ==="

aws rds create-db-instance \
    --region "$REGION" \
    --db-instance-identifier "$RDS_IDENTIFIER" \
    --engine postgres \
    --db-instance-class db.t3.micro \
    --allocated-storage 20 \
    --storage-type gp2 \
    --db-name "$DB_NAME" \
    --master-username "$DB_USERNAME" \
    --manage-master-user-password \
    --db-subnet-group-name "$DB_SUBNET_GROUP" \
    --vpc-security-group-ids "$SECURITY_GROUP_ID" \
    --no-publicly-accessible \
    --backup-retention-period 0 \
    --tags Key=Name,Value=TallerAWS-CLI-RDS

echo "RDS solicitado: $RDS_IDENTIFIER"

echo "Esperando a que RDS esté disponible..."

aws rds wait db-instance-available \
    --region "$REGION" \
    --db-instance-identifier "$RDS_IDENTIFIER"

echo "RDS listo."


# =========================
# Resumen
# =========================

echo
echo "======================================"
echo "      RECURSOS CREADOS CORRECTAMENTE"
echo "======================================"

echo "S3:  $BUCKET_NAME"
echo "EC2: $INSTANCE_ID"
echo "RDS: $RDS_IDENTIFIER"
echo "EC2 IP pública: $PUBLIC_IP"
echo
echo "Todos los recursos están listos."