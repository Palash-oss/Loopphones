"""Telemetry data API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime, timedelta

from db.database import get_db
from models.database import TelemetrySnapshot, Device
from models.schemas import TelemetryCreate, TelemetryResponse
from services.ml.health_predictor import health_predictor

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("/", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    telemetry_data: TelemetryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Ingest telemetry data from Guardian app."""
    # Verify device exists
    result = await db.execute(
        select(Device).where(Device.id == telemetry_data.device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {telemetry_data.device_id} not found"
        )
    
    # Get recent telemetry for prediction
    recent_result = await db.execute(
        select(TelemetrySnapshot)
        .where(TelemetrySnapshot.device_id == telemetry_data.device_id)
        .order_by(desc(TelemetrySnapshot.timestamp))
        .limit(30)
    )
    recent_telemetry = recent_result.scalars().all()
    
    # Prepare history for ML prediction
    telemetry_history = [
        {
            'timestamp': t.timestamp,
            'battery_cycle_count': t.battery_cycle_count,
            'battery_health_percentage': t.battery_health_percentage,
            'battery_temperature': t.battery_temperature,
            'thermal_events_count': t.thermal_events_count,
            'crash_count': t.crash_count,
        }
        for t in recent_telemetry
    ]
    
    # Add current data
    telemetry_history.append({
        'timestamp': datetime.utcnow(),
        'battery_cycle_count': telemetry_data.battery_cycle_count,
        'battery_health_percentage': telemetry_data.battery_health_percentage,
        'battery_temperature': telemetry_data.battery_temperature,
        'thermal_events_count': telemetry_data.thermal_events_count,
        'crash_count': telemetry_data.crash_count,
    })
    
    # Run ML prediction
    prediction = await health_predictor.predict_rul(telemetry_history)
    
    # Create telemetry snapshot
    snapshot = TelemetrySnapshot(
        **telemetry_data.model_dump(),
        predicted_rul_days=prediction['predicted_rul_days'],
        failure_probability=prediction['failure_probability']
    )
    
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    
    return snapshot


@router.get("/{device_id}", response_model=List[TelemetryResponse])
async def get_telemetry_history(
    device_id: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get telemetry history for a device."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(TelemetrySnapshot)
        .where(TelemetrySnapshot.device_id == device_id)
        .where(TelemetrySnapshot.timestamp >= cutoff_date)
        .order_by(TelemetrySnapshot.timestamp)
    )
    
    snapshots = result.scalars().all()
    
    if not snapshots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for device {device_id}"
        )
    
    return snapshots


@router.get("/{device_id}/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent telemetry snapshot."""
    result = await db.execute(
        select(TelemetrySnapshot)
        .where(TelemetrySnapshot.device_id == device_id)
        .order_by(desc(TelemetrySnapshot.timestamp))
        .limit(1)
    )
    
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for device {device_id}"
        )
    
    return snapshot
