"""Digital Passport API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from db.database import get_db
from models.database import DigitalPassport, Device
from models.schemas import PassportCreate, PassportResponse, LifecycleEvent
from services.blockchain.solana_service import get_solana_service
from config.settings import settings

router = APIRouter(prefix="/passports", tags=["Digital Passports"])


@router.post("/", response_model=PassportResponse, status_code=status.HTTP_201_CREATED)
async def create_passport(
    passport_data: PassportCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a Digital Passport NFT for a device."""
    # Verify device exists
    result = await db.execute(
        select(Device).where(Device.id == passport_data.device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {passport_data.device_id} not found"
        )
    
    # Check if passport already exists
    result = await db.execute(
        select(DigitalPassport).where(DigitalPassport.device_id == passport_data.device_id)
    )
    existing_passport = result.scalar_one_or_none()
    
    if existing_passport:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Passport already exists for device {passport_data.device_id}"
        )
    
    # Mint NFT on Solana
    solana_service = get_solana_service(
        settings.SOLANA_RPC_URL,
        settings.SOLANA_PRIVATE_KEY,
        settings.SOLANA_NETWORK
    )
    
    metadata = {
        'device_id': device.id,
        'model': device.model,
        'manufacturer': device.manufacturer,
        'purchase_date': device.purchase_date.isoformat()
    }
    
    mint_result = await solana_service.mint_passport(
        device_id=device.id,
        owner_address=passport_data.owner_address,
        metadata=metadata
    )
    
    # Create passport record
    passport_id = f"PASS-{device.id}"
    passport = DigitalPassport(
        id=passport_id,
        device_id=device.id,
        mint_address=mint_result['mint_address'],
        owner_address=passport_data.owner_address,
        circularity_score=70,  # Base score
        lifecycle_events=[{
            'event_type': 'minted',
            'timestamp': datetime.utcnow().isoformat(),
            'description': 'Digital Passport created',
            'metadata': mint_result
        }],
        carbon_footprint=solana_service.calculate_carbon_footprint()
    )
    
    db.add(passport)
    
    # Update device with passport info
    device.passport_id = passport_id
    device.passport_mint_address = mint_result['mint_address']
    
    await db.commit()
    await db.refresh(passport)
    
    return passport


@router.get("/{passport_id}", response_model=PassportResponse)
async def get_passport(
    passport_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Digital Passport by ID."""
    result = await db.execute(
        select(DigitalPassport).where(DigitalPassport.id == passport_id)
    )
    passport = result.scalar_one_or_none()
    
    if not passport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passport {passport_id} not found"
        )
    
    return passport


@router.get("/device/{device_id}", response_model=PassportResponse)
async def get_passport_by_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Digital Passport by device ID."""
    result = await db.execute(
        select(DigitalPassport).where(DigitalPassport.device_id == device_id)
    )
    passport = result.scalar_one_or_none()
    
    if not passport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No passport found for device {device_id}"
        )
    
    return passport


@router.post("/{passport_id}/events", response_model=PassportResponse)
async def add_lifecycle_event(
    passport_id: str,
    event: LifecycleEvent,
    db: AsyncSession = Depends(get_db)
):
    """Add a lifecycle event to the passport."""
    result = await db.execute(
        select(DigitalPassport).where(DigitalPassport.id == passport_id)
    )
    passport = result.scalar_one_or_none()
    
    if not passport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passport {passport_id} not found"
        )
    
    # Record event on blockchain
    solana_service = get_solana_service(
        settings.SOLANA_RPC_URL,
        settings.SOLANA_PRIVATE_KEY,
        settings.SOLANA_NETWORK
    )
    
    blockchain_result = await solana_service.record_lifecycle_event(
        mint_address=passport.mint_address,
        event_type=event.event_type,
        event_data=event.model_dump()
    )
    
    # Add to lifecycle events
    lifecycle_events = passport.lifecycle_events or []
    lifecycle_events.append({
        **event.model_dump(),
        'blockchain_tx': blockchain_result['transaction_signature']
    })
    passport.lifecycle_events = lifecycle_events
    
    # Update counters and scores
    if event.event_type == 'repair':
        passport.total_repairs += 1
    elif event.event_type == 'refurbishment':
        passport.total_refurbishments += 1
    elif event.event_type == 'parts_harvested':
        passport.parts_harvested += 1
    elif event.event_type == 'recycling':
        passport.recycling_events += 1
    
    # Recalculate circularity score
    device_result = await db.execute(
        select(Device).where(Device.id == passport.device_id)
    )
    device = device_result.scalar_one()
    usage_years = (datetime.utcnow() - device.purchase_date).days / 365
    
    passport.circularity_score = solana_service.calculate_circularity_score(
        repairs=passport.total_repairs,
        refurbishments=passport.total_refurbishments,
        parts_harvested=passport.parts_harvested,
        recycling_events=passport.recycling_events,
        usage_years=usage_years
    )
    
    # Recalculate carbon footprint
    passport.carbon_footprint = solana_service.calculate_carbon_footprint(
        usage_years=usage_years,
        repairs=passport.total_repairs,
        refurbishments=passport.total_refurbishments,
        parts_harvested=passport.parts_harvested
    )
    
    await db.commit()
    await db.refresh(passport)
    
    return passport
