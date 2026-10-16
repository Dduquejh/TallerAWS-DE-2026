import boto3
import requests
from requests_aws4auth import AWS4Auth

REGION = "us-east-2"
ENDPOINT = (
    "https://taller-neptune-instance.c1aymgwc63hv.us-east-2."
    "neptune.amazonaws.com:8182"
)

session = boto3.Session(region_name=REGION)
credentials = session.get_credentials()

if credentials is None:
    raise RuntimeError("No se encontraron credenciales AWS.")

credentials = credentials.get_frozen_credentials()

auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    "neptune-db",
    session_token=credentials.token,
)


def gremlin(query):
    response = requests.post(
        f"{ENDPOINT}/gremlin",
        auth=auth,
        json={"gremlin": query},
        timeout=60,
    )

    if not response.ok:
        print("Consulta:", query)
        print("Respuesta:", response.text)
        response.raise_for_status()

    body = response.json()
    return body.get("result", {}).get("data", [])


def mostrar_resultados(titulo, query):
    print(f"\n{'=' * 60}")
    print(titulo)
    print("=" * 60)

    resultados = gremlin(query)

    if not resultados:
        print("Sin resultados.")
        return

    # Neptune puede devolver los resultados dentro de @value.
    if isinstance(resultados, dict):
        resultados = resultados.get("@value", [resultados])

    for resultado in resultados:
        if isinstance(resultado, dict) and "@value" in resultado:
            resultado = resultado["@value"]

        if isinstance(resultado, dict):
            datos = {}
            for clave, valor in resultado.items():
                if isinstance(valor, dict):
                    valor = valor.get("@value", valor)
                datos[clave] = valor
            print(" | ".join(f"{clave}: {valor}" for clave, valor in datos.items()))
        else:
            print(resultado)


def main():
    # Consulta 1: personas y vehículos en los que viajan.
    mostrar_resultados(
        "1. PERSONAS Y VEHICULOS",
        """
        g.V().hasLabel('persona')
         .as('persona')
         .out('VIAJA_EN').as('vehiculo')
         .select('persona', 'vehiculo')
         .by('nombre')
        """,
    )

    # Consulta 2: personas y sus destinos.
    mostrar_resultados(
        "2. PERSONAS Y DESTINOS",
        """
        g.V().hasLabel('persona')
         .as('persona')
         .out('DESTINO').as('destino')
         .select('persona', 'destino')
         .by('nombre')
        """,
    )

    # Consulta 3: vehículos y lugares a los que conectan.
    mostrar_resultados(
        "3. VEHICULOS Y LUGARES CONECTADOS",
        """
        g.V().hasLabel('vehiculo')
         .as('vehiculo')
         .out('CONECTA').as('lugar')
         .select('vehiculo', 'lugar')
         .by('nombre')
        """,
    )

    # Consulta 4: recorrido de una persona a través de su vehículo.
    mostrar_resultados(
        "4. RECORRIDO: PERSONA -> VEHICULO -> LUGAR",
        """
        g.V().hasLabel('persona')
         .as('persona')
         .out('VIAJA_EN').as('vehiculo')
         .out('CONECTA').as('lugar')
         .select('persona', 'vehiculo', 'lugar')
         .by('nombre')
        """,
    )


if __name__ == "__main__":
    main()