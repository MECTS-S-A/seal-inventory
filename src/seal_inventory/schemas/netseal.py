from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NetsealCreate(BaseModel):
    NET_ID: str
    VENDOR: Optional[str]
    NET_STATUS: Optional[str]
    OWNER_ID: Optional[str]
    OWNER_NAME: Optional[str]
    OWNER_PROVINCE: Optional[str]
    OWNER_REGION: Optional[str]


class NetsealUpdate(BaseModel):
    VENDOR: Optional[str]
    NET_STATUS: Optional[str]
    OWNER_NAME: Optional[str]
    OWNER_PROVINCE: Optional[str]
    OWNER_REGION: Optional[str]


class NetsealResponse(BaseModel):
    ID: int
    NET_ID: str
    VENDOR: Optional[str]
    NET_STATUS: Optional[str]
    OWNER_NAME: Optional[str]
    CREATED: Optional[datetime]


class NetsealStatsResponse(BaseModel):
    total: int
    in_use: int
    available: int
    to_change: int
    compensation: int
    maintenance: int