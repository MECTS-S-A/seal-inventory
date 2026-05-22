from fastapi import APIRouter, Depends, HTTPException

from seal_inventory.api.seals.seal_routes import service
from seal_inventory.services.netseal_service import NetsealService
from seal_inventory.schemas.netseal import NetsealCreate, NetsealUpdate, TransferRejectRequest, TransferCreateRequest
from seal_inventory.core.dependencies import get_current_user
from seal_inventory.schemas.netseal import NetsealStatsResponse


router = APIRouter(prefix="/api/v1/netseals", tags=["netseal"])


def get_service():
    return NetsealService()


@router.post("/")
def create(data: NetsealCreate, user=Depends(get_current_user), service=Depends(get_service)):
    service.create(data.dict(), user)
    return {"message": "Created"}


@router.get("/")
def list_all(service=Depends(get_service)):
    return service.list()


@router.get("/{id}")
def get_one(id: int, service=Depends(get_service)):
    return service.get(id)


@router.put("/{id}")
def update(id: int, data: NetsealUpdate, user=Depends(get_current_user), service=Depends(get_service)):
    service.update(id, data.dict(), user)
    return {"message": "Updated"}


@router.delete("/{id}")
def delete(id: int, service=Depends(get_service)):
    service.delete(id)
    return {"message": "Deleted"}


@router.get("/analytical/stats", response_model=NetsealStatsResponse)
def get_stats(service=Depends(get_service)):
    try:
        return service.get_stats()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch netseal stats")

@router.post("/tranfer")
async def create_transfer(
        payload: TransferCreateRequest,
        user=Depends(get_current_user),
):
    transfer_id = await service.create_transfer(
        payload,
        user,
    )

    return {
        "id": transfer_id,
        "status": "pending",
    }


@router.patch("/{transfer_id}/confirm")
async def confirm_transfer(
        transfer_id: int,
        user=Depends(get_current_user),
):
    await service.confirm_transfer(
        transfer_id,
        user,
    )

    return {"success": True}


@router.patch("/{transfer_id}/reject")
async def reject_transfer(
        transfer_id: int,
        payload: TransferRejectRequest,
        user=Depends(get_current_user),
):
    await service.reject_transfer(
        transfer_id,
        user,
        payload.reason,
    )

    return {"success": True}