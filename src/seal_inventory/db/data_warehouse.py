from typing import Any, Iterable, Callable
from seal_inventory.db.connection import get_dwh_connection


class SqlServerDataWarehouse:

    def __init__(self, connection_factory: Callable = get_dwh_connection):
        self.connection_factory = connection_factory

    def fetch_scalar(self, query: str, parameters: Iterable[Any] = ()) -> Any:
        with self.connection_factory() as connection:
            cursor = connection.cursor()
            cursor.execute(query, *tuple(parameters))
            row = cursor.fetchone()
            return None if row is None else row[0]

    def fetch_rows(self, query: str, parameters: Iterable[Any] = ()) -> list[dict]:
        with self.connection_factory() as connection:
            cursor = connection.cursor()
            cursor.execute(query, *tuple(parameters))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]