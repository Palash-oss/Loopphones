"""Device grading API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from db.database import get_db
from models.database import GradingRecord, Device
from models.schemas import GradingRequest, GradingResponse
from services.ml.grading_engine import grading_engine

router = APIRouter(prefix="/grading", tags=["Grading"])


@router.post("/", response_model=GradingResponse, status_code=status.HTTP_201_CREATED)
async def grade_device(
    grading_request: GradingRequest,
    db: AsyncSession = Depends(get_db)
):
    """Grade device condition from images."""
    # Verify device exists
    result = await db.execute(
        select(Device).where(Device.id == grading_request.device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {grading_request.device_id} not found"
        )
    
    # Run grading engine
    grading_result = await grading_engine.grade_device(grading_request.image_urls)
    
    # Save grading record
    grading_record = GradingRecord(
        device_id=grading_request.device_id,
        grade=grading_result['grade'],
        confidence_score=grading_result['confidence_score'],
        screen_scratches_count=grading_result['screen_scratches_count'],
        screen_cracks_count=grading_result['screen_cracks_count'],
        body_scratches_count=grading_result['body_scratches_count'],
        body_dents_count=grading_result['body_dents_count'],
        image_urls=grading_request.image_urls,
        cv_model_version=grading_result['cv_model_version'],
        detection_results=grading_result['detection_results']
    )
    
    db.add(grading_record)
    await db.commit()
    await db.refresh(grading_record)
    
    # Update device status
    device.status = "graded"
    await db.commit()
    
    return grading_record


@router.get("/{device_id}", response_model=List[GradingResponse])
async def get_grading_history(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get grading history for a device."""
    result = await db.execute(
        select(GradingRecord)
        .where(GradingRecord.device_id == device_id)
        .order_by(desc(GradingRecord.timestamp))
    )
    
    grading_records = result.scalars().all()
    
    if not grading_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No grading records found for device {device_id}"
        )
    
    return grading_records


@router.get("/{device_id}/latest", response_model=GradingResponse)
async def get_latest_grading(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent grading record."""
    result = await db.execute(
        select(GradingRecord)
        .where(GradingRecord.device_id == device_id)
        .order_by(desc(GradingRecord.timestamp))
        .limit(1)
    )
    
    grading_record = result.scalar_one_or_none()
    
    if not grading_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No grading records found for device {device_id}"
        )
    
    return grading_record
