"""Database models using SQLAlchemy ORM."""
from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Device(Base):
    """Device model representing registered devices."""
    __tablename__ = "devices"
    
    id = Column(String, primary_key=True)  # IMEI/Serial
    model = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    purchase_date = Column(TIMESTAMP, nullable=False)
    current_owner = Column(String)
    status = Column(String)  # active, graded, refurbished, recycled
    storage_gb = Column(Integer)
    ram_gb = Column(Integer)
    original_battery_capacity = Column(Integer)
    passport_id = Column(String, unique=True)
    passport_mint_address = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class TelemetrySnapshot(Base):
    """Telemetry snapshot model for device health data."""
    __tablename__ = "telemetry_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    battery_cycle_count = Column(Integer)
    battery_health_percentage = Column(Float)
    battery_voltage = Column(Float)
    battery_temperature = Column(Float)
    cpu_throttling_events = Column(Integer)
    thermal_events_count = Column(Integer)
    crash_count = Column(Integer)
    predicted_rul_days = Column(Integer)  # ML prediction
    failure_probability = Column(Float)


class GradingRecord(Base):
    """Grading record model for device condition assessment."""
    __tablename__ = "grading_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    grade = Column(String)  # excellent, good, fair, poor
    confidence_score = Column(Float)
    screen_scratches_count = Column(Integer)
    screen_cracks_count = Column(Integer)
    body_scratches_count = Column(Integer)
    body_dents_count = Column(Integer)
    image_urls = Column(JSON)
    cv_model_version = Column(String)
    detection_results = Column(JSON)  # Raw YOLO output


class PriceEstimate(Base):
    """Price estimate model for device valuation."""
    __tablename__ = "price_estimates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    estimated_resale_price = Column(Float)
    market_average_price = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    model_version = Column(String)
    feature_importance = Column(JSON)


class DigitalPassport(Base):
    """Digital passport model for blockchain-tracked device lifecycle."""
    __tablename__ = "digital_passports"
    
    id = Column(String, primary_key=True)
    device_id = Column(String, ForeignKey("devices.id"), unique=True, nullable=False)
    mint_address = Column(String, unique=True)
    owner_address = Column(String)
    circularity_score = Column(Integer, default=70)
    total_repairs = Column(Integer, default=0)
    total_refurbishments = Column(Integer, default=0)
    parts_harvested = Column(Integer, default=0)
    recycling_events = Column(Integer, default=0)
    lifecycle_events = Column(JSON)  # Array of events
    carbon_footprint = Column(Float)  # kg CO2e
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
