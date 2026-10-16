import boto3
import requests
from requests_aws4auth import AWS4Auth

# ============================================================
# CONFIGURACION DE NEPTUNE
# ============================================================

REGION = "us-east-2"

ENDPOINT = (
    "https://taller-neptune-instance."
    "c1aymgwc63hv.us-east-2.neptune.amazonaws.com:8182"
)

session = boto3.Session(region_name=REGION)
credentials = session.get_credentials()

if credentials is None:
    raise RuntimeError(
        "No se encontraron credenciales AWS. "
        "Verifica tu perfil default de AWS CLI."
    )

credentials = credentials.get_frozen_credentials()

auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    "neptune-db",
    session_token=credentials.token,
)

# ============================================================
# FUNCION PARA EJECUTAR CONSULTAS GREMLIN
# ============================================================

def gremlin(query):
    response = requests.post(
        f"{ENDPOINT}/gremlin",
        auth=auth,
        json={"gremlin": query},
        timeout=60,
    )

    if not response.ok:
        print("\nERROR AL EJECUTAR GREMLIN")
        print("Consulta:", query)
        print("Codigo HTTP:", response.status_code)
        print("Respuesta:", response.text)
        response.raise_for_status()

    return response.json()


def get_count(query):
    result = gremlin(query)
    data = result.get("result", {}).get("data", [])

    def extract(value):
        if isinstance(value, dict):
            if "@value" in value:
                return extract(value["@value"])
            if "value" in value:
                return extract(value["value"])

        if isinstance(value, list):
            if len(value) == 1:
                return extract(value[0])
            raise ValueError(
                f"Se esperaba un único conteo, pero llegó una lista: {value}"
            )

        if isinstance(value, (int, float, str)):
            return int(value)

        raise ValueError(f"Formato de conteo inesperado: {value!r}")

    try:
        return extract(data)
    except (ValueError, TypeError):
        print("Respuesta completa de Neptune:", repr(result))
        raise


# ============================================================
# VERTICES: 4 PERSONAS, 3 VEHICULOS Y 3 LUGARES
# ============================================================

vertices = [
    ("persona", "ana", "Ana"),
    ("persona", "luis", "Luis"),
    ("persona", "marta", "Marta"),
    ("persona", "juan", "Juan"),
    ("vehiculo", "bus1", "Bus1"),
    ("vehiculo", "bus2", "Bus2"),
    ("vehiculo", "van1", "Van1"),
    ("lugar", "universidad", "Universidad"),
    ("lugar", "estacion", "Estacion"),
    ("lugar", "centro", "Centro"),
]

# ============================================================
# ARISTAS: 15 RELACIONES
# ============================================================

aristas = [
    ("ana", "VIAJA_EN", "bus1"),
    ("luis", "VIAJA_EN", "bus1"),
    ("marta", "VIAJA_EN", "bus2"),
    ("juan", "VIAJA_EN", "van1"),

    ("ana", "DESTINO", "universidad"),
    ("luis", "DESTINO", "centro"),
    ("marta", "DESTINO", "estacion"),
    ("juan", "DESTINO", "universidad"),

    ("bus1", "CONECTA", "universidad"),
    ("bus1", "CONECTA", "estacion"),
    ("bus2", "CONECTA", "estacion"),
    ("bus2", "CONECTA", "centro"),
    ("van1", "CONECTA", "universidad"),
    ("van1", "CONECTA", "centro"),

    ("juan", "CONDUCE", "bus1"),
]


# ============================================================
# CONSTRUIR EL GRAFO
# ============================================================

def main():
    print("Conectando con Amazon Neptune...")
    print("Endpoint:", ENDPOINT)

    # IMPORTANTE:
    # Este comando elimina TODOS los vertices y aristas
    # del grafo actual. Usalo solo para este laboratorio.
    print("\nLimpiando el grafo anterior...")
    gremlin("g.V().drop()")

    # Crear vertices con IDs internos estables.
    print("\nCreando vertices...")

    for tipo, identificador, nombre in vertices:
        query = (
            f"g.addV('{tipo}')"
            f".property(T.id, '{identificador}')"
            f".property('nombre', '{nombre}')"
        )

        gremlin(query)
        print(f"  Vertice creado: {nombre} ({tipo})")

    # Crear aristas buscando los vertices por su ID interno.
    print("\nCreando aristas...")

    for origen, relacion, destino in aristas:
        query = (
            f"g.V('{origen}')"
            f".addE('{relacion}')"
            f".to(__.V('{destino}'))"
        )

        gremlin(query)
        print(f"  {origen} -[{relacion}]-> {destino}")

    # Verificar los conteos.
    print("\nVerificando el grafo...")

    total_vertices = get_count("g.V().count()")
    total_aristas = get_count("g.E().count()")

    print("\n================================")
    print("RESULTADO DE LA CARGA")
    print("================================")
    print(f"Vertices: {total_vertices}")
    print(f"Aristas:  {total_aristas}")

    if total_vertices == 10 and total_aristas == 15:
        print("Grafo creado correctamente.")
    else:
        print("ADVERTENCIA: los conteos no coinciden con lo esperado.")


if __name__ == "__main__":
    main()
