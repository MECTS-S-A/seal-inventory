"""API route definitions."""

from __future__ import annotations
from fastapi import Depends

from fastapi import APIRouter, HTTPException, Query

from seal_inventory.schemas.seal import (
    HealthResponse,
    TableListResponse,
    TableRowsResponse, ESealInventoryResponse, ESealStatsResponse,
)
from seal_inventory.services.seal_service import SealService

router = APIRouter()
v1_router  = APIRouter(prefix="/api/v1/seals", tags=["seal"])
service = SealService()

def get_service() -> SealService:
    return SealService()

@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Basic service health endpoint."""

    return HealthResponse(status="ok", detail="API is running")


@router.get("/db/health", response_model=HealthResponse, tags=["database"])
def database_health() -> HealthResponse:
    """Verify SQL Server connectivity."""

    try:
        service.get_database_health()
    except Exception as exc:  # pragma: no cover - external dependency path
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return HealthResponse(status="ok", detail="Database connection succeeded")


@router.get("/tables", response_model=TableListResponse, tags=["database"])
def get_tables() -> TableListResponse:
    """Return available tables from the configured schema."""

    try:
        tables = service.get_tables()
    except Exception as exc:  # pragma: no cover - external dependency path
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TableListResponse(schema=service.get_schema_name(), tables=tables)


@router.get("/tables/{table_name}/rows", response_model=TableRowsResponse, tags=["data"])
def get_table_rows(
    table_name: str,
    limit: int = Query(default=100, ge=1, le=1000),
) -> TableRowsResponse:
    """Return rows from a specific table."""

    try:
        rows = service.get_table_rows(table_name=table_name, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - external dependency path
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TableRowsResponse(table_name=table_name, row_count=len(rows), rows=rows)

@router.get("/eseals", response_model=ESealInventoryResponse, tags=["eseal"])
def get_eseals(
        limit: int = Query(default=100, ge=1, le=1000),
        service: SealService = Depends(get_service),
):
    try:
        data = service.get_eseal_inventory(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch eseal inventory")

    return {
        "count": len(data),
        "data": data,
    }

@router.get("/eseals/stats", response_model=ESealStatsResponse, tags=["eseal"],)
def get_eseal_stats(service: SealService = Depends(get_service)):
    try:
        return service.get_eseal_stats()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch eseal stats")

v1_router.include_router(router)
