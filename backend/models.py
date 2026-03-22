"""Pydantic response schemas for the CropGuard API."""

from __future__ import annotations

from pydantic import BaseModel


class DiseaseResult(BaseModel):
    name: str
    confidence: float
    severity: str  # Mild | Moderate | Severe | Critical
    affected_percent: float
    description: str
    spread_risk: str = "Medium"  # Low | Medium | High


class NutrientRecommendation(BaseModel):
    nutrient: str
    symptom: str
    treatment: str
    frequency: str
    organic_option: str


class NutrientResult(BaseModel):
    deficiencies: list[str]
    recommendations: list[NutrientRecommendation]


class WateringAdvice(BaseModel):
    current_status: str
    schedule: str
    amount_ml_per_plant: int
    warning: str | None = None


class PestResult(BaseModel):
    detected: bool
    type: str | None = None
    severity: str | None = None
    treatment: str | None = None


class SoilAdvice(BaseModel):
    recommended_ph: str
    amendments: list[str]
    drainage: str


class CarePlan(BaseModel):
    immediate: list[str]
    this_week: list[str]
    ongoing: list[str]


class ScanResponse(BaseModel):
    scan_id: str
    crop_type: str
    disease: DiseaseResult
    mask_url: str
    nutrients: NutrientResult
    watering: WateringAdvice
    pests: PestResult
    soil: SoilAdvice
    care_plan: CarePlan
    recovery_outlook: str


class ScanSummary(BaseModel):
    scan_id: str
    timestamp: str
    crop_type: str
    disease_name: str
    severity: str
    thumbnail_url: str


class HealthResponse(BaseModel):
    status: str
    plugins: list[str]
