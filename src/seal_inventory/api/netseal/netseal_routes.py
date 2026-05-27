from fastapi import APIRouter, Depends, HTTPException

from seal_inventory.services.netseal_service import NetsealService
from seal_inventory.schemas.netseal import (
    NetsealCreate,
    NetsealUpdate,
    NetsealStatsResponse,
    TransferCreateRequest,
    TransferRejectRequest,
)
from seal_inventory.core.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/netseals",
    tags=["netseal"],
)


def get_service():
    return NetsealService()


# =====================================================
# NETSEAL CRUD
# =====================================================

@router.post("/")
def create(
        data: NetsealCreate,
        user=Depends(get_current_user),
        service: NetsealService = Depends(get_service),
):
    service.create(
        data.dict(),
        user["username"],
    )

    return {
        "message": "Created"
    }


@router.get("/")
def list_all(
        service: NetsealService = Depends(get_service),
):
    return service.list()


@router.get("/analytical/stats", response_model=NetsealStatsResponse)
def get_stats(
        service: NetsealService = Depends(get_service),
):
    return service.get_stats()


@router.get("/{id}")
def get_one(
        id: int,
        service: NetsealService = Depends(get_service),
):
    return service.get(id)


@router.put("/{id}")
def update(
        id: int,
        data: NetsealUpdate,
        user=Depends(get_current_user),
        service: NetsealService = Depends(get_service),
):
    service.update(
        id,
        data.dict(),
        user["username"],
    )

    return {
        "message": "Updated"
    }


@router.delete("/{id}")
def delete(
        id: int,
        service: NetsealService = Depends(get_service),
):
    service.delete(id)

    return {
        "message": "Deleted"
    }


# =====================================================
# TRANSFERS
# =====================================================

@router.post("/transfers")
async def create_transfer(
        payload: TransferCreateRequest,
        user=Depends(get_current_user),
        service: NetsealService = Depends(get_service),
):
    try:

        transfer_id = await service.create_transfer(
            payload,
            user["username"],
        )

        return {
            "id": transfer_id,
            "status": "pending",
        }

    except Exception as e:

        print(
            "TRANSFER ERROR:",
            str(e),
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.patch("/transfers/{transfer_id}/confirm")
async def confirm_transfer(
        transfer_id: int,
        user=Depends(get_current_user),
        service: NetsealService = Depends(get_service),
):
    try:

        await service.confirm_transfer(
            transfer_id,
            user["username"],
        )

        return {
            "success": True,
            "status": "confirmed",
        }

    except Exception as e:

        print(
            "CONFIRM ERROR:",
            str(e),
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.patch("/transfers/{transfer_id}/reject")
async def reject_transfer(
        transfer_id: int,
        payload: TransferRejectRequest,
        user=Depends(get_current_user),
        service: NetsealService = Depends(get_service),
):
    try:

        await service.reject_transfer(
            transfer_id,
            user["username"],
            payload.reason,
        )

        return {
            "success": True,
            "status": "rejected",
        }

    except Exception as e:

        print(
            "REJECT ERROR:",
            str(e),
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )