"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class DeviceStatus(str, Enum):
    ACTIVE = "active"
    GRADED = "graded"
    REFURBISHED = "refurbished"
    RECYCLED = "recycled"
    PARTS_HARVESTED = "parts_harvested"


class Grade(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


# Device Schemas
class DeviceCreate(BaseModel):
    id: str = Field(..., description="IMEI or Serial Number")
    model: str
    manufacturer: str
    purchase_date: datetime
    current_owner: Optional[str] = None
    storage_gb: int
    ram_gb: int
    original_battery_capacity: int


class DeviceResponse(BaseModel):
    id: str
    model: str
    manufacturer: str
    purchase_date: datetime
    current_owner: Optional[str]
    status: Optional[str]
    storage_gb: int
    ram_gb: int
    original_battery_capacity: int
    passport_id: Optional[str]
    passport_mint_address: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Telemetry Schemas
class TelemetryCreate(BaseModel):
    device_id: str
    battery_cycle_count: int
    battery_health_percentage: float
    battery_voltage: float
    battery_temperature: float
    cpu_throttling_events: int = 0
    thermal_events_count: int = 0
    crash_count: int = 0


class TelemetryResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    battery_cycle_count: int
    battery_health_percentage: float
    battery_voltage: float
    battery_temperature: float
    cpu_throttling_events: int
    thermal_events_count: int
    crash_count: int
    predicted_rul_days: Optional[int]
    failure_probability: Optional[float]

    class Config:
        from_attributes = True


# Grading Schemas
class GradingRequest(BaseModel):
    device_id: str
    image_urls: List[str] = Field(..., description="URLs of device images")


class DamageDetection(BaseModel):
    type: str
    count: int
    confidence: float
    bounding_boxes: List[Dict[str, float]]


class GradingResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    grade: str
    confidence_score: float
    screen_scratches_count: int
    screen_cracks_count: int
    body_scratches_count: int
    body_dents_count: int
    image_urls: List[str]
    cv_model_version: str
    detection_results: Dict[str, Any]

    class Config:
        from_attributes = True


# Pricing Schemas
class PricingRequest(BaseModel):
    device_id: str
    age_days: int
    storage_gb: int
    ram_gb: int
    battery_health: float
    battery_cycles: int
    grade_score: int = Field(..., ge=1, le=4, description="1=Poor, 4=Excellent")
    screen_damage_score: int = Field(..., ge=0, le=10)
    body_damage_score: int = Field(..., ge=0, le=10)


class PriceEstimateResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    estimated_resale_price: float
    market_average_price: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    model_version: str
    feature_importance: Dict[str, float]

    class Config:
        from_attributes = True


# Digital Passport Schemas
class PassportCreate(BaseModel):
    device_id: str
    owner_address: str


class LifecycleEvent(BaseModel):
    event_type: str
    timestamp: datetime
    description: str
    metadata: Optional[Dict[str, Any]] = None


class PassportResponse(BaseModel):
    id: str
    device_id: str
    mint_address: Optional[str]
    owner_address: str
    circularity_score: int
    total_repairs: int
    total_refurbishments: int
    parts_harvested: int
    recycling_events: int
    lifecycle_events: List[LifecycleEvent]
    carbon_footprint: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analysis Schemas
class HealthPrediction(BaseModel):
    predicted_rul_days: int
    failure_probability: float
    degradation_rate: float
    confidence_score: float


class DeviceAnalysisResponse(BaseModel):
    device_id: str
    timestamp: datetime
    health_prediction: HealthPrediction
    grading: Optional[GradingResponse]
    price_estimate: Optional[PriceEstimateResponse]
    recommendation: str
    action_required: bool
    recommended_actions: List[str]


# Recommendation
class Recommendation(BaseModel):
    action: str
    priority: str  # high, medium, low
    estimated_value: Optional[float]
    reasoning: str
