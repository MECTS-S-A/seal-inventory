from seal_inventory.repositories.netseal_repository import NetsealRepository


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