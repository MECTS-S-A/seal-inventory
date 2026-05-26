from seal_inventory.repositories.netseal_repository import NetsealRepository
from typing import List
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

        payload.origin_site_id = origin["owner_id"]

        transfer_id = self.repo.create_transfer(
            payload,
            sender_username,
        )

        await manager.send_to_owner(
            payload.destination_site_id,
            {
                "type": "TRANSFER_INCOMING",
                "transfer_id": transfer_id,
                "net_ids": payload.net_ids,
                "sender": sender_username,
                "from": origin["owner_id"],
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

        self.repo.confirm_transfer(
            transfer_id,
            receiver_username,
        )

        await manager.send_to_owner(
            str(transfer["ORIGIN_SITE_ID"]),
            {
                "type": "TRANSFER_UPDATE",
                "transfer_id": transfer_id,
                "action": "confirmed",
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

        self.repo.reject_transfer(
            transfer_id,
            receiver_username,
            reason,
        )

        await manager.send_to_owner(
            str(transfer["ORIGIN_SITE_ID"]),
            {
                "type": "TRANSFER_UPDATE",
                "transfer_id": transfer_id,
                "action": "rejected",
                "reason": reason,
            },
        )