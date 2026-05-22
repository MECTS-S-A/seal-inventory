"""FastAPI application bootstrap."""

from __future__ import annotations
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from seal_inventory.api.seals.seal_routes import v1_router
from seal_inventory.api.auth.auth_routes import auth_router
from seal_inventory.api.netseal.netseal_routes import router as netseal_router
from seal_inventory.api.websocket_routes import router as websocket_router


def validate_env() -> None:
    """Validate required database settings before startup."""

    required = [
        "DB_DRIVER",
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DWH_DB_NAME",
        "INV_DB_NAME",
    ]

    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")


validate_env()

app = FastAPI(
    title=os.getenv("APP_NAME", "Seal Inventory API"),
    version="0.1.0",
    description="API service for retrieving existing records from Microsoft SQL Server.",
)

# Routers
app.include_router(v1_router)
app.include_router(auth_router)
app.include_router(netseal_router)
app.include_router(websocket_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)