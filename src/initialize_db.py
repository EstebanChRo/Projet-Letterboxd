from postgres_utils import PostgreSQLClient
from db_schema import TABLE_DEFINITIONS


def initialize_db() -> None:
    client = PostgreSQLClient()
    if not client.connect():
        raise ConnectionError("Impossible de se connecter à la base de données PostgreSQL.")

    if client.create_tables(TABLE_DEFINITIONS):
        print("Schéma de base de données créé avec succès.")
    else:
        print("Échec lors de la création du schéma de base de données.")

    client.disconnect()
