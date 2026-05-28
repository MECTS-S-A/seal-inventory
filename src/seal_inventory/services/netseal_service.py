from seal_inventory.repositories.netseal_repository import NetsealRepository
from seal_inventory.websocket_manager import manager


class NetsealService:

    def __init__(self):
        self.repo = NetsealRepository()

    def create(self, data, user):
        data["CREATED_BY"] = user
        self.repo.create(data)

    def list(self):
        return self.repo.get_all()

    def get(self, id):
        data = self.repo.get_by_id(id)

        if not data:
            raise ValueError("Netseal not found")

        return data

    def update(self, id, data, user):
        data["UPDATED_BY"] = user
        self.repo.update(id, data)

    def delete(self, id):
        self.repo.delete(id)

    def get_stats(self):
        stats = self.repo.get_stats()

        return {
            "total": stats.get("total", 0),
            "in_use": stats.get("in_use", 0),
            "available": stats.get("available", 0),
            "to_change": stats.get("to_change", 0),
            "compensation": stats.get("compensation", 0),
            "maintenance": stats.get("maintenance", 0),
        }

    async def create_transfer(
            self,
            payload,
            sender_username,
    ):
        origin = self.repo.get_owner_by_net(
            payload.net_ids[0]
        )

        transfer_id = self.repo.create_transfer(
            payload=payload,
            sender_username=sender_username,
            origin_site_id=origin["owner_id"],
            origin_location=origin["owner_region"],
        )

        # Notify receiver
        await manager.send_to_user(
            payload.receiver_username,
            {
                "type": "TRANSFER_INCOMING",
                "transfer_id": transfer_id,
                "sender": sender_username,
                "receiver": payload.receiver_username,
                "net_ids": payload.net_ids,
                "origin_site_id": origin["owner_id"],
                "origin_location": origin["owner_region"],
                "origin_name": origin["owner_name"],
                "destination_site_id": payload.destination_site_id,
                "destination_location": payload.destination_location,
            },
        )

        # Notify sender
        await manager.send_to_user(
            sender_username,
            {
                "type": "TRANSFER_CREATED",
                "transfer_id": transfer_id,
                "receiver": payload.receiver_username,
                "net_ids": payload.net_ids,
            },
        )

        return transfer_id

    async def confirm_transfer(
            self,
            transfer_id,
            receiver_username,
    ):
        transfer = self.repo.get_transfer(
            transfer_id
        )

        if not transfer:
            raise ValueError(
                "Transfer not found"
            )

        self.repo.confirm_transfer(
            transfer_id,
            receiver_username,
        )

        # Notify sender
        await manager.send_to_user(
            transfer["sender_username"],
            {
                "type": "TRANSFER_CONFIRMED",
                "transfer_id": transfer_id,
                "receiver": receiver_username,
            },
        )

        # Notify receiver
        await manager.send_to_user(
            receiver_username,
            {
                "type": "TRANSFER_RECEIVED",
                "transfer_id": transfer_id,
            },
        )

    async def reject_transfer(
            self,
            transfer_id,
            receiver_username,
            reason,
    ):
        transfer = self.repo.get_transfer(
            transfer_id
        )

        if not transfer:
            raise ValueError(
                "Transfer not found"
            )

        self.repo.reject_transfer(
            transfer_id,
            receiver_username,
            reason,
        )

        # Notify sender
        await manager.send_to_user(
            transfer["sender_username"],
            {
                "type": "TRANSFER_REJECTED",
                "transfer_id": transfer_id,
                "receiver": receiver_username,
                "reason": reason,
            },
        )

        # Notify receiver
        await manager.send_to_user(
            receiver_username,
            {
                "type": "TRANSFER_REJECTION_SENT",
                "transfer_id": transfer_id,
                "reason": reason,
            },
        )