from fastapi import APIRouter, Depends, HTTPException
from seal_inventory.services.netseal_service import NetsealService
from seal_inventory.schemas.netseal import NetsealCreate, NetsealUpdate
from seal_inventory.core.dependencies import get_current_user
from seal_inventory.schemas.netseal import NetsealStatsResponse, NetsealTransferRequest


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

@router.post("/transfer")
def transfer_netseals(
        payload: NetsealTransferRequest,
        user=Depends(get_current_user),
        service: NetsealService = Depends(get_service),
):
    try:
        updated = service.transfer_netseals(
            netseal_ids=payload.netseal_ids,
            site=payload.site,
            location=payload.location,
            user=user,
        )

        return {
            "message": "Transfer completed successfully",
            "updated_records": updated,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )