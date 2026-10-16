import boto3
import requests
from requests_aws4auth import AWS4Auth

REGION = "us-east-2"
ENDPOINT = (
    "https://taller-neptune-instance."
    "c1aymgwc63hv.us-east-2.neptune.amazonaws.com:8182"
)

session = boto3.Session(region_name=REGION)
credentials = session.get_credentials().get_frozen_credentials()

auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    "neptune-db",
    session_token=credentials.token,
)

response = requests.post(
    f"{ENDPOINT}/gremlin",
    auth=auth,
    json={"gremlin": "g.V().count()"},
    timeout=30,
)

print("HTTP:", response.status_code)
print(response.text)
response.raise_for_status()
