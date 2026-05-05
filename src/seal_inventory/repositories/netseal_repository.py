from seal_inventory.db.connection import get_inventory_connection


class NetsealRepository:

    def create(self, data):
        query = """
                INSERT INTO asset.net_inventory (
                    NET_ID, VENDOR, NET_STATUS, OWNER_ID, OWNER_NAME,
                    OWNER_PROVINCE, OWNER_REGION, CREATED, CREATED_BY
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?) \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                data["NET_ID"],
                data.get("VENDOR"),
                data.get("NET_STATUS"),
                data.get("OWNER_ID"),
                data.get("OWNER_NAME"),
                data.get("OWNER_PROVINCE"),
                data.get("OWNER_REGION"),
                data.get("CREATED_BY", "system"),
            )
            conn.commit()

    def get_all(self):
        query = "SELECT * FROM asset.net_inventory"

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        query = "SELECT * FROM asset.net_inventory WHERE ID = ?"

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, id)
            row = cursor.fetchone()
            if not row:
                return None
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

    def update(self, id: int, data):
        query = """
                UPDATE asset.net_inventory
                SET VENDOR=?, NET_STATUS=?, OWNER_NAME=?, OWNER_PROVINCE=?, OWNER_REGION=?,
                    UPDATED=GETDATE(), UPDATED_BY=?
                WHERE ID=? \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                data.get("VENDOR"),
                data.get("NET_STATUS"),
                data.get("OWNER_NAME"),
                data.get("OWNER_PROVINCE"),
                data.get("OWNER_REGION"),
                data.get("UPDATED_BY", "system"),
                id,
            )
            conn.commit()

    def delete(self, id: int):
        query = "DELETE FROM asset.net_inventory WHERE ID = ?"

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, id)
            conn.commit()

    def get_stats(self):
        query = """
                SELECT
                    COUNT(*) AS total,

                    SUM(CASE WHEN NET_STATUS = 'Em Uso' THEN 1 ELSE 0 END) AS in_use,

                    SUM(CASE WHEN NET_STATUS = 'Disponivel' THEN 1 ELSE 0 END) AS available,

                    SUM(CASE WHEN NET_STATUS = 'Por Substituir' THEN 1 ELSE 0 END) AS to_change,

                    SUM(CASE WHEN NET_STATUS = 'Em Transporte' THEN 1 ELSE 0 END) AS compensation,

                    SUM(CASE
                            WHEN NET_STATUS IN ('Em Transferencia', 'Em Manutencao', 'Danificado')
                                THEN 1 ELSE 0
                        END) AS maintenance

                FROM asset.net_inventory \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()

            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))