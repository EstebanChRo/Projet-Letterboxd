import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
import os

class PostgreSQLClient:
    """
    Une classe pour gérer les interactions avec une base de données PostgreSQL.

    Attributes:
        host (str): Adresse du serveur PostgreSQL.
        database (str): Nom de la base de données.
        user (str): Nom d'utilisateur pour la connexion.
        password (str): Mot de passe pour la connexion.
        port (str): Port de la base de données.
        connection: Objet de connexion à la base de données.
    """

    def __init__(self):
        """
        Initialise la classe avec les paramètres de connexion.
        """
        load_dotenv()
        self._host = "localhost"
        self._database = os.getenv("POSTGRES_DB")
        self._user = os.getenv("POSTGRES_USER")
        self._password = os.getenv("POSTGRES_PASSWORD")
        self._port = "5432"
        self._connection = None

    def connect(self) -> bool:
        """
        Établit une connexion à la base de données PostgreSQL.

        Returns:
            bool: True si la connexion est réussie, False sinon.
        """
        try:
            self._connection = psycopg2.connect(
                host=self._host,
                database=self._database,
                user=self._user,
                password=self._password,
                port=self._port
            )
            print("Connexion à PostgreSQL réussie.")
            return True
        except psycopg2.Error as e:
            print(f"Erreur de connexion à PostgreSQL : {e}")
            return False

    def disconnect(self) -> None:
        """
        Ferme la connexion à la base de données.
        """
        if self._connection:
            self._connection.close()
            print("Connexion à PostgreSQL fermée.")

    def execute_query(self, query: Union[str, sql.Composed], params: Optional[tuple] = None) -> bool:
        """
        Exécute une requête SQL (INSERT, UPDATE, DELETE, etc.).

        Args:
            query: Requête SQL à exécuter.
            params: Paramètres pour la requête (optionnel).

        Returns:
            bool: True si la requête est exécutée avec succès, False sinon.
        """
        if not self._connection:
            print("Pas de connexion active à la base de données.")
            return False

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, params)
                self._connection.commit()
                print("Requête exécutée avec succès.")
                return True
        except psycopg2.Error as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")
            self._connection.rollback()
            return False

    def fetch_query(self, query: Union[str, sql.Composed], params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Exécute une requête SQL de type SELECT et retourne les résultats.

        Args:
            query: Requête SQL à exécuter.
            params: Paramètres pour la requête (optionnel).

        Returns:
            List[Dict[str, Any]]: Liste de dictionnaires représentant les lignes retournées.
        """
        if not self._connection:
            print("Pas de connexion active à la base de données.")
            return []

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except psycopg2.Error as e:
            print(f"Erreur lors de la récupération des données : {e}")
            return []

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Crée une table dans la base de données.

        Args:
            table_name: Nom de la table à créer.
            columns: Dictionnaire où les clés sont les noms des colonnes et les valeurs sont les types de données.

        Returns:
            bool: True si la table est créée avec succès, False sinon.
        """
        columns_def = ", ".join([f"{name} {type}" for name, type in columns.items()])
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_def)
        )
        return self.execute_query(query)

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """
        Insère une ligne de données dans une table.

        Args:
            table_name: Nom de la table cible.
            data: Dictionnaire où les clés sont les noms des colonnes et les valeurs sont les données à insérer.

        Returns:
            bool: True si l'insertion est réussie, False sinon.
        """
        columns = data.keys()
        values = tuple(data.values())
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join([sql.Placeholder()] * len(columns))
        )
        return self.execute_query(query, values)

    def create_tables(self, table_definitions: Dict[str, str]) -> bool:
        """
        Crée une série de tables dans la base de données.

        Args:
            table_definitions: Dictionnaire où les clés sont les noms des tables et les valeurs sont les requêtes SQL de création.

        Returns:
            bool: True si toutes les tables ont été créées avec succès, False sinon.
        """
        for table_name, query in table_definitions.items():
            print(f"Création de la table {table_name}...")
            if not self.execute_query(query):
                print(f"Échec de la création de la table {table_name}.")
                return False
        return True