import os
import logging
from contextlib import contextmanager
from typing import Any, Optional

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PostgreSQLClient:
    """
    Client PostgreSQL avec gestion de connexion.
    Charge les variables d'environnement depuis un fichier .env :
        - POSTGRES_USER
        - POSTGRES_PASSWORD
        - POSTGRES_DB
        - POSTGRES_HOST  (optionnel, défaut: localhost)
        - POSTGRES_PORT  (optionnel, défaut: 5432)
    """

    def __init__(self):
        self._config = {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "dbname": os.getenv("POSTGRES_DB"),
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
        }
        self._connection: Optional[psycopg2.extensions.connection] = None

    def connect(self) -> None:
        """Ouvre la connexion à la base de données si elle n'est pas déjà ouverte."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(**self._config)
            logger.debug("Connexion PostgreSQL établie.")

    def disconnect(self) -> None:
        """Ferme proprement la connexion."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.debug("Connexion PostgreSQL fermée.")

    @contextmanager
    def _get_cursor(self, cursor_factory=psycopg2.extras.RealDictCursor):
        """
        Context manager interne : fournit un curseur et gère commit/rollback.
        Réutilise la connexion existante (pas de nouvelle connexion à chaque appel).
        Arg:
            cursor_factory: Classe de curseur pour le format des résultats (défaut: RealDictCursor).   
        """
        self.connect()
        cursor = self._connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()


    def execute(
        self,
        query: str,
        params: Optional[tuple | dict] = None,
        fetch: str = "all",
    ) -> Any:
        """
        Exécute une seule requête SQL.
        Args:
            query: Requête SQL (utiliser %s ou %(name)s pour les paramètres).
            params: Paramètres de la requête (tuple ou dict).
            fetch: "all"  → liste de toutes les lignes (SELECT)  
                    "one"  → première ligne uniquement, retourne un dict si j'attend une seule rép
                    "none" → pas de retour (INSERT / UPDATE / DELETE)
        Returns:
            Liste de dict, un dict, ou None selon `fetch`.
        """
        with self._get_cursor() as cur:
            cur.execute(query, params)
            if fetch == "all":
                return cur.fetchall()
            if fetch == "one":
                return cur.fetchone()
            return None

    def execute_many(
        self,
        queries: list[dict],
    ) -> list[Any]:
        """
        Exécute plusieurs requêtes en un seul aller-retour base de données
        (éco-conception : une seule transaction, un seul commit).
        Args:
            queries : Liste de dicts, chacun avec :
                        - "query"  (str)            : requête SQL
                        - "params" (tuple|dict|None): paramètres (optionnel)
                        - "fetch"  (str)            : "all" | "one" | "none"
                                                    (optionnel, défaut "none")
        Returns:
            Liste des résultats dans le même ordre que `queries`.
            Les entrées avec fetch="none" retournent None.
        Exemple:
        ```python
            results = client.execute_many([
                {"query": "INSERT INTO ...", "params": (...,), "fetch": "none"},
                {"query": "SELECT ...",      "params": (...,), "fetch": "all"},
            ])
        ```
        """
        results = []
        with self._get_cursor() as cur:
            for item in queries:
                query = item["query"]
                params = item.get("params")
                fetch = item.get("fetch", "none")
                cur.execute(query, params)
                if fetch == "all":
                    results.append(cur.fetchall())
                elif fetch == "one":
                    results.append(cur.fetchone())
                else:
                    results.append(None)
        return results

    def execute_values(
        self,
        query: str,
        values: list[tuple],
        fetch: str = "none",
        page_size: int = 1000,
    ) -> Any:
        """
        Insère / met à jour plusieurs lignes en un seul appel base de données
        via psycopg2.extras.execute_values.
        Args:
            query     : Requête avec placeholder %s pour le bloc VALUES,
                        ex. "INSERT INTO table (a, b) VALUES %s"
            values    : Liste de tuples à insérer.
            fetch     : "all" | "none"
            page_size : Nombre de lignes par batch interne (défaut 1000).
        Returns:
            Résultat fetchall() si fetch="all", sinon None.
        """
        with self._get_cursor() as cur:
            psycopg2.extras.execute_values(
                cur, query, values, fetch=fetch == "all", page_size=page_size
            )
            if fetch == "all":
                return cur.fetchall()
            return None

    def fetch_all(self, table: str, conditions: Optional[dict] = None) -> list[dict]:
        """
        Récupère toutes les lignes d'une table avec des filtres optionnels.
        Args:
            table      : Nom de la table.
            conditions : Dict {colonne: valeur} utilisé comme clause WHERE (AND).
        Returns:
            Liste de dicts représentant les lignes.
        """
        query = f"SELECT * FROM {table}"  # noqa: S608
        params = None
        if conditions:
            clauses = " AND ".join(f"{col} = %s" for col in conditions)
            query += f" WHERE {clauses}"
            params = tuple(conditions.values())
        return self.execute(query, params, fetch="all")

    def insert(self, table: str, data: dict, returning: Optional[str] = None) -> Any:
        """
        Insère une ligne dans une table.
        Args:
            table     : Nom de la table.
            data      : Dict {colonne: valeur}.
            returning : Nom de la colonne à retourner (ex. "id"), ou None.
        Returns:
            La valeur de la colonne `returning` si précisée, sinon None.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        if returning:
            query += f" RETURNING {returning}"
        row = self.execute(query, tuple(data.values()), fetch="one" if returning else "none")
        return row[returning] if returning and row else None

    def update(
        self,
        table: str,
        data: dict,
        conditions: dict,
    ) -> None:
        """
        Met à jour des lignes dans une table.
        Args:
            table      : Nom de la table.
            data       : Dict {colonne: nouvelle_valeur}.
            conditions : Dict {colonne: valeur} pour la clause WHERE.
        """
        set_clause = ", ".join(f"{col} = %s" for col in data)
        where_clause = " AND ".join(f"{col} = %s" for col in conditions)
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(conditions.values())
        self.execute(query, params, fetch="none")

    def delete(self, table: str, conditions: dict) -> None:
        """
        Supprime des lignes dans une table.
        Args:
            table      : Nom de la table.
            conditions : Dict {colonne: valeur} pour la clause WHERE.
        """
        where_clause = " AND ".join(f"{col} = %s" for col in conditions)
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.execute(query, tuple(conditions.values()), fetch="none")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False