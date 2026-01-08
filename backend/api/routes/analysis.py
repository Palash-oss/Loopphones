"""Device analysis API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from db.database import get_db
from services.analysis_service import device_analysis_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/{device_id}")
async def analyze_device(
    device_id: str,
    include_grading: bool = True,
    include_pricing: bool = True,
    image_urls: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform comprehensive device analysis.
    
    Orchestrates all ML engines:
    - Hardware health prediction (TFT)
    - Surface grading (YOLO)
    - Price estimation (XGBoost)
    - Recommendations
    """
    try:
        analysis_report = await device_analysis_service.analyze_device(
            device_id=device_id,
            db=db,
            include_grading=include_grading,
            include_pricing=include_pricing,
            image_urls=image_urls
        )
        
        return analysis_report
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{device_id}/health")
async def get_health_analysis(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get only hardware health analysis."""
    try:
        analysis_report = await device_analysis_service.analyze_device(
            device_id=device_id,
            db=db,
            include_grading=False,
            include_pricing=False
        )
        
        return {
            'device_id': device_id,
            'health_prediction': analysis_report['health_prediction'],
            'device_info': analysis_report['device_info']
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{device_id}/recommendations")
async def get_recommendations(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get device recommendations."""
    try:
        analysis_report = await device_analysis_service.analyze_device(
            device_id=device_id,
            db=db,
            include_grading=True,
            include_pricing=True
        )
        
        return {
            'device_id': device_id,
            'recommendations': analysis_report['recommendations'],
            'timestamp': analysis_report['timestamp']
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
