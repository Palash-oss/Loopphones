"""Device management API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.database import get_db
from models.database import Device
from models.schemas import DeviceCreate, DeviceResponse

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new device in the system."""
    # Check if device already exists
    result = await db.execute(
        select(Device).where(Device.id == device_data.id)
    )
    existing_device = result.scalar_one_or_none()
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with ID {device_data.id} already exists"
        )
    
    # Create new device
    device = Device(
        **device_data.model_dump(),
        status="active"
    )
    
    db.add(device)
    await db.commit()
    await db.refresh(device)
    
    return device


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get device by ID."""
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    return device


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all devices with optional filtering."""
    query = select(Device)
    
    if status_filter:
        query = query.where(Device.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return devices


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a device."""
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    await db.delete(device)
    await db.commit()
    
    return None
