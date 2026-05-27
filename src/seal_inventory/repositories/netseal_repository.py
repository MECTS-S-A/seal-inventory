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

    def create_transfer(
            self,
            payload,
            sender_username: str,
            origin_site_id: str,
            origin_location: str,
    ):
        query = """
                INSERT INTO asset.transfers (
                    net_ids,
                    origin_site_id,
                    origin_location,
                    destination_site_id,
                    destination_location,
                    sender_username,
                    receiver_username,
                    status,
                    created_at,
                    updated_at
                )
                    OUTPUT INSERTED.id
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    'pending',
                    GETDATE(),
                    GETDATE()
                    ) \
                """

        with get_inventory_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                query,

                ",".join(payload.net_ids),

                origin_site_id,
                origin_location,

                payload.destination_site_id,
                payload.destination_location,

                sender_username,
                payload.receiver_username,
            )

            transfer_id = cursor.fetchone()[0]

            conn.commit()

            return transfer_id

    def confirm_transfer(
            self,
            transfer_id: int,
            receiver_username: str,
    ):
        query = """
                UPDATE asset.transfers
                SET
                    STATUS='confirmed',
                    receiver_username=?,
                    updated_at=GETDATE()
                WHERE id=? \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                query,
                receiver_username,
                transfer_id,
            )

            conn.commit()

    def reject_transfer(
            self,
            transfer_id: int,
            receiver_username: str,
            reason: str,
    ):
        query = """
                UPDATE asset.transfers
                SET
                    status='rejected',
                    receiver_username=?,
                    reason=?,
                    updated_at=GETDATE()
                WHERE ID=? \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                query,
                receiver_username,
                reason,
                transfer_id,
            )

            conn.commit()


    def get_owner_by_net(
            self,
            net_id: str,
    ):
        query = """
                SELECT TOP 1
        OWNER_ID,
                    OWNER_NAME,
                       OWNER_REGION
                FROM asset.net_inventory
                WHERE NET_ID = ? \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(query, net_id)

            row = cursor.fetchone()

            if not row:
                raise ValueError(
                    f"Net seal {net_id} not found"
                )

            return {
                "owner_id": str(row[0]),
                "owner_name": row[1],
                "owner_region": row[2],
            }

    def get_transfer(
            self,
            transfer_id: int,
    ):
        query = """
                SELECT *
                FROM asset.transfers
                WHERE ID = ? \
                """

        with get_inventory_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(query, transfer_id)

            row = cursor.fetchone()
    
            if not row:
                return None

            columns = [c[0] for c in cursor.description]

            return dict(zip(columns, row))

    def get_transfer(
            self,
            transfer_id: int,
    ):
        query = """
                SELECT *
                FROM asset.transfers
                WHERE id = ? \
                """

        with get_inventory_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                query,
                transfer_id,
            )

            row = cursor.fetchone()

            if not row:
                return None

            columns = [
                col[0].lower()
                for col in cursor.description
            ]

            return dict(
                zip(columns, row)
            )


    def get_user_transfers(
            self,
            username: str,
    ):
        query = """
                SELECT *
                FROM asset.transfers
                WHERE receiver_username = ?
                ORDER BY created_at DESC \
                """

        with get_inventory_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, username)

            columns = [
                col[0].lower()
                for col in cursor.description
            ]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]