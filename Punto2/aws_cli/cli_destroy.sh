#!/usr/bin/env bash

set -e

# =========================
# Configuración
# =========================

REGION="us-east-2"

BUCKET_NAME="talleraws-de-2026-573992724610-cli"

RDS_IDENTIFIER="talleraws-cli-rds"

# =========================
# EC2
# =========================

echo "=== Eliminando EC2 ==="

INSTANCE_ID=$(aws ec2 describe-instances \
    --region "$REGION" \
    --filters \
        "Name=tag:Name,Values=TallerAWS-CLI-EC2" \
        "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

if [ "$INSTANCE_ID" != "None" ] && [ -n "$INSTANCE_ID" ]; then

    echo "EC2 encontrado: $INSTANCE_ID"

    aws ec2 terminate-instances \
        --region "$REGION" \
        --instance-ids "$INSTANCE_ID"

    echo "Esperando a que EC2 termine..."

    aws ec2 wait instance-terminated \
        --region "$REGION" \
        --instance-ids "$INSTANCE_ID"

    echo "EC2 eliminado."

else

    echo "No se encontró el EC2."
fi


# =========================
# RDS
# =========================

echo
echo "=== Eliminando RDS ==="

if aws rds describe-db-instances \
    --region "$REGION" \
    --db-instance-identifier "$RDS_IDENTIFIER" \
    >/dev/null 2>&1; then

    echo "RDS encontrado: $RDS_IDENTIFIER"

    aws rds delete-db-instance \
        --region "$REGION" \
        --db-instance-identifier "$RDS_IDENTIFIER" \
        --skip-final-snapshot \
        --delete-automated-backups

    echo "Esperando a que RDS sea eliminado..."

    aws rds wait db-instance-deleted \
        --region "$REGION" \
        --db-instance-identifier "$RDS_IDENTIFIER"

    echo "RDS eliminado."

else

    echo "No se encontró el RDS."
fi


# =========================
# S3
# =========================

echo
echo "=== Eliminando S3 ==="

if aws s3api head-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    >/dev/null 2>&1; then

    echo "Bucket encontrado: $BUCKET_NAME"

    echo "Eliminando objetos..."

    aws s3 rm \
        "s3://$BUCKET_NAME" \
        --recursive

    echo "Eliminando bucket..."

    aws s3api delete-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION"

    echo "S3 eliminado."

else

    echo "El bucket no existe."
fi


# =========================
# Verificación
# =========================

echo
echo "======================================"
echo "       VERIFICANDO ELIMINACIÓN"
echo "======================================"

echo
echo "S3:"

if aws s3api head-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    >/dev/null 2>&1; then

    echo "ERROR: el bucket todavía existe."

else

    echo "OK: el bucket fue eliminado."
fi


echo
echo "RDS:"

if aws rds describe-db-instances \
    --region "$REGION" \
    --db-instance-identifier "$RDS_IDENTIFIER" \
    >/dev/null 2>&1; then

    echo "ERROR: el RDS todavía existe."

else

    echo "OK: el RDS fue eliminado."
fi


echo
echo "EC2:"

REMAINING_INSTANCE=$(aws ec2 describe-instances \
    --region "$REGION" \
    --filters \
        "Name=tag:Name,Values=TallerAWS-CLI-EC2" \
        "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[].Instances[].InstanceId' \
    --output text)

if [ -n "$REMAINING_INSTANCE" ]; then

    echo "ERROR: todavía existe un EC2: $REMAINING_INSTANCE"

else

    echo "OK: el EC2 fue eliminado."
fi

echo
echo "Proceso de eliminación terminado."