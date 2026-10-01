import boto3
import json


def get_secret(secret_name):
    client = boto3.client("secretsmanager")

    response = client.get_secret_value(
        SecretId=secret_name
    )

    return json.loads(response["SecretString"])


secret = get_secret("arn:aws:secretsmanager:us-east-2:573992724610:secret:prueba/app-demo-ziLxZ7")

print(f"Username: {secret['username']}, Password: {secret['password']}")