"""Device analysis orchestration service."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from models.database import Device, TelemetrySnapshot, GradingRecord, PriceEstimate
from services.ml.health_predictor import health_predictor
from services.ml.grading_engine import grading_engine
from services.ml.pricing_engine import pricing_engine

logger = logging.getLogger(__name__)


class DeviceAnalysisService:
    """
    Orchestrates all ML engines to provide comprehensive device analysis.
    
    Coordinates:
    - Hardware health prediction
    - Surface grading
    - Price estimation
    - Recommendations
    """
    
    async def analyze_device(
        self,
        device_id: str,
        db: AsyncSession,
        include_grading: bool = True,
        include_pricing: bool = True,
        image_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete device analysis.
        
        Args:
            device_id: Device identifier
            db: Database session
            include_grading: Whether to run grading analysis
            include_pricing: Whether to run pricing analysis
            image_urls: Device images for grading
        
        Returns:
            Comprehensive analysis report
        """
        logger.info(f"Starting analysis for device {device_id}")
        
        # 1. Get device info
        device = await self._get_device(device_id, db)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        # 2. Get telemetry history (last 30 days)
        telemetry_history = await self._get_telemetry_history(device_id, db, days=30)
        
        # 3. Run health prediction
        health_prediction = await health_predictor.predict_rul(telemetry_history)
        
        # 4. Run grading (if requested and images provided)
        grading_result = None
        if include_grading and image_urls:
            grading_result = await grading_engine.grade_device(image_urls)
            # Save to database
            await self._save_grading_record(device_id, grading_result, db)
        elif include_grading:
            # Get most recent grading
            grading_result = await self._get_latest_grading(device_id, db)
        
        # 5. Run pricing (if requested)
        price_estimate = None
        if include_pricing:
            price_estimate = await self._estimate_price(
                device, telemetry_history, grading_result, db
            )
        
        # 6. Generate recommendations
        recommendations = await self._generate_recommendations(
            device, health_prediction, grading_result, price_estimate
        )
        
        # 7. Compile comprehensive report
        analysis_report = {
            'device_id': device_id,
            'timestamp': datetime.utcnow().isoformat(),
            'device_info': {
                'model': device.model,
                'manufacturer': device.manufacturer,
                'age_days': (datetime.utcnow() - device.purchase_date).days,
                'status': device.status,
            },
            'health_prediction': health_prediction,
            'grading': grading_result,
            'price_estimate': price_estimate,
            'recommendations': recommendations,
        }
        
        logger.info(f"Analysis complete for device {device_id}")
        return analysis_report
    
    async def _get_device(self, device_id: str, db: AsyncSession) -> Optional[Device]:
        """Retrieve device from database."""
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_telemetry_history(
        self, device_id: str, db: AsyncSession, days: int = 30
    ) -> List[Dict]:
        """Get telemetry history for specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(TelemetrySnapshot)
            .where(TelemetrySnapshot.device_id == device_id)
            .where(TelemetrySnapshot.timestamp >= cutoff_date)
            .order_by(TelemetrySnapshot.timestamp)
        )
        
        snapshots = result.scalars().all()
        
        return [
            {
                'timestamp': s.timestamp,
                'battery_cycle_count': s.battery_cycle_count,
                'battery_health_percentage': s.battery_health_percentage,
                'battery_temperature': s.battery_temperature,
                'thermal_events_count': s.thermal_events_count,
                'crash_count': s.crash_count,
            }
            for s in snapshots
        ]
    
    async def _get_latest_grading(
        self, device_id: str, db: AsyncSession
    ) -> Optional[Dict]:
        """Get most recent grading record."""
        result = await db.execute(
            select(GradingRecord)
            .where(GradingRecord.device_id == device_id)
            .order_by(desc(GradingRecord.timestamp))
            .limit(1)
        )
        
        grading = result.scalar_one_or_none()
        if not grading:
            return None
        
        return {
            'grade': grading.grade,
            'confidence_score': grading.confidence_score,
            'screen_scratches_count': grading.screen_scratches_count,
            'screen_cracks_count': grading.screen_cracks_count,
            'body_scratches_count': grading.body_scratches_count,
            'body_dents_count': grading.body_dents_count,
            'timestamp': grading.timestamp.isoformat(),
        }
    
    async def _save_grading_record(
        self, device_id: str, grading_result: Dict, db: AsyncSession
    ):
        """Save grading record to database."""
        grading_record = GradingRecord(
            device_id=device_id,
            grade=grading_result['grade'],
            confidence_score=grading_result['confidence_score'],
            screen_scratches_count=grading_result['screen_scratches_count'],
            screen_cracks_count=grading_result['screen_cracks_count'],
            body_scratches_count=grading_result['body_scratches_count'],
            body_dents_count=grading_result['body_dents_count'],
            image_urls=grading_result.get('image_urls', []),
            cv_model_version=grading_result['cv_model_version'],
            detection_results=grading_result['detection_results'],
        )
        db.add(grading_record)
        await db.commit()
    
    async def _estimate_price(
        self,
        device: Device,
        telemetry_history: List[Dict],
        grading_result: Optional[Dict],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Estimate device price."""
        # Get latest telemetry
        latest_telemetry = telemetry_history[-1] if telemetry_history else {}
        
        # Calculate age
        age_days = (datetime.utcnow() - device.purchase_date).days
        
        # Grade score mapping
        grade_scores = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1}
        grade_score = 3  # Default to good
        screen_damage = 0
        body_damage = 0
        
        if grading_result:
            grade_score = grade_scores.get(grading_result.get('grade', 'good'), 3)
            screen_damage = (
                grading_result.get('screen_scratches_count', 0) * 2 +
                grading_result.get('screen_cracks_count', 0) * 5
            )
            body_damage = (
                grading_result.get('body_scratches_count', 0) * 1 +
                grading_result.get('body_dents_count', 0) * 3
            )
        
        # Estimate price
        price_estimate = await pricing_engine.estimate_price(
            device_model=device.model,
            manufacturer=device.manufacturer,
            age_days=age_days,
            storage_gb=device.storage_gb or 128,
            ram_gb=device.ram_gb or 6,
            battery_health=latest_telemetry.get('battery_health_percentage', 85),
            battery_cycles=latest_telemetry.get('battery_cycle_count', 100),
            grade_score=grade_score,
            screen_damage_score=min(screen_damage, 10),
            body_damage_score=min(body_damage, 10),
        )
        
        # Save to database
        price_record = PriceEstimate(
            device_id=device.id,
            estimated_resale_price=price_estimate['estimated_resale_price'],
            market_average_price=price_estimate['market_average_price'],
            confidence_interval_lower=price_estimate['confidence_interval_lower'],
            confidence_interval_upper=price_estimate['confidence_interval_upper'],
            model_version=price_estimate['model_version'],
            feature_importance=price_estimate['feature_importance'],
        )
        db.add(price_record)
        await db.commit()
        
        return price_estimate
    
    async def _generate_recommendations(
        self,
        device: Device,
        health_prediction: Dict,
        grading_result: Optional[Dict],
        price_estimate: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations."""
        recommendations = []
        priority = "medium"
        action_required = False
        
        # Health-based recommendations
        rul_days = health_prediction.get('predicted_rul_days', 365)
        failure_prob = health_prediction.get('failure_probability', 0.1)
        
        if rul_days < 30:
            recommendations.append({
                'action': 'immediate_refurbishment',
                'priority': 'high',
                'reasoning': f'Device has only {rul_days} days of estimated life remaining',
                'estimated_value': price_estimate.get('estimated_resale_price', 0) * 0.5 if price_estimate else None
            })
            priority = "high"
            action_required = True
        elif rul_days < 90:
            recommendations.append({
                'action': 'schedule_maintenance',
                'priority': 'medium',
                'reasoning': f'Device health declining, {rul_days} days RUL',
                'estimated_value': None
            })
            action_required = True
        
        if failure_prob > 0.7:
            recommendations.append({
                'action': 'parts_harvesting',
                'priority': 'high',
                'reasoning': f'High failure probability ({failure_prob:.1%}), harvest valuable components',
                'estimated_value': price_estimate.get('estimated_resale_price', 0) * 0.3 if price_estimate else None
            })
            priority = "high"
            action_required = True
        
        # Grade-based recommendations
        if grading_result:
            grade = grading_result.get('grade')
            if grade == 'excellent':
                recommendations.append({
                    'action': 'resale',
                    'priority': 'high',
                    'reasoning': 'Device in excellent condition, optimal for resale',
                    'estimated_value': price_estimate.get('estimated_resale_price') if price_estimate else None
                })
            elif grade == 'poor':
                recommendations.append({
                    'action': 'recycling',
                    'priority': 'medium',
                    'reasoning': 'Poor condition, consider recycling for materials recovery',
                    'estimated_value': 50.0  # Base recycling value
                })
        
        # Default recommendation
        if not recommendations:
            recommendations.append({
                'action': 'continue_monitoring',
                'priority': 'low',
                'reasoning': 'Device in good health, continue normal operation',
                'estimated_value': None
            })
        
        return {
            'primary_action': recommendations[0]['action'] if recommendations else 'continue_monitoring',
            'priority': priority,
            'action_required': action_required,
            'recommendations': recommendations,
            'summary': f"Device has {rul_days} days RUL with {failure_prob:.1%} failure probability"
        }


# Singleton instance
device_analysis_service = DeviceAnalysisService()
