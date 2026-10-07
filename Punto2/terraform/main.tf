# Configuración de terraform
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# Configuración de proveedor y región
provider "aws" {
  region = "us-east-2"
}

# Configuración de componentes de red
locals {
  vpc_id            = "vpc-0f97d7e96864377f2"
  subnet_id         = "subnet-096a4967a3ea16daa"
  security_group_id = "sg-01cd7b4a43ef5a50c"
  db_subnet_group   = "default-vpc-0f97d7e96864377f2"
  ami_id            = "ami-0ca656964bac97e7f"
}


# Obtener ID de la cuenta
data "aws_caller_identity" "current" {}

# Creación del bucket de S3
resource "aws_s3_bucket" "taller" {
  bucket = "talleraws-de-2026-${data.aws_caller_identity.current.account_id}"
}


# Creación de EC2
resource "aws_instance" "taller" {
  ami           = local.ami_id
  instance_type = "t3.micro"

  subnet_id                   = local.subnet_id
  vpc_security_group_ids      = [local.security_group_id]
  associate_public_ip_address = true

  tags = {
    Name = "TallerAWS-Terraform-EC2"
  }
}


# Creación de RDS
resource "aws_db_instance" "taller" {
  identifier = "talleraws-terraform-rds"

  engine         = "postgres"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "talleraws"
  username = "dbuser"

  manage_master_user_password = true

  db_subnet_group_name   = local.db_subnet_group
  vpc_security_group_ids = [local.security_group_id]

  publicly_accessible = false

  skip_final_snapshot = true

  tags = {
    Name = "TallerAWS-Terraform-RDS"
  }
}
