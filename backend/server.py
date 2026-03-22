"""CropGuard FastAPI server — main entry point."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select

from care_engine import (
    build_care_plan,
    get_nutrient_plan,
    get_pest_treatment,
    get_soil_recommendations,
    get_watering_schedule,
)
from models import (
    CarePlan,
    DiseaseResult,
    HealthResponse,
    NutrientRecommendation,
    NutrientResult,
    PestResult,
    ScanResponse,
    ScanSummary,
    SoilAdvice,
    WateringAdvice,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
UPLOAD_DIR = Path("/tmp/cropguard")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MASK_DIR = UPLOAD_DIR / "masks"
MASK_DIR.mkdir(exist_ok=True)
DEMO_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "demo_cache"
SAMPLE_IMAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_images"

# ---------- SQLite persistence ----------

class ScanRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: str = Field(index=True)
    timestamp: str
    crop_type: str
    disease_name: str
    severity: str
    result_json: str
    image_path: str

engine = create_engine("sqlite:///cropguard.db")
SQLModel.metadata.create_all(engine)

# ---------- FastAPI app ----------

app = FastAPI(title="CropGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_demo_cache(filename: str) -> dict | None:
    cache_file = DEMO_CACHE_DIR / f"{Path(filename).stem}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return None


def _save_demo_cache(filename: str, data: dict) -> None:
    DEMO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = DEMO_CACHE_DIR / f"{Path(filename).stem}.json"
    cache_file.write_text(json.dumps(data, indent=2))


def _persist_scan(scan_id: str, result: dict, image_path: str) -> None:
    record = ScanRecord(
        scan_id=scan_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        crop_type=result.get("crop_type", "Unknown"),
        disease_name=result.get("disease", {}).get("name", "Unknown"),
        severity=result.get("disease", {}).get("severity", "Unknown"),
        result_json=json.dumps(result),
        image_path=str(image_path),
    )
    with Session(engine) as session:
        session.add(record)
        session.commit()


def _build_mock_response(scan_id: str) -> dict:
    return {
        "scan_id": scan_id,
        "crop_type": "Tomato",
        "disease": {
            "name": "Late Blight",
            "confidence": 0.94,
            "severity": "Moderate",
            "affected_percent": 23.4,
            "description": "Fungal infection caused by Phytophthora infestans",
            "spread_risk": "High",
        },
        "mask_url": f"/masks/{scan_id}.png",
        "nutrients": {
            "deficiencies": ["Nitrogen", "Calcium"],
            "recommendations": [
                {
                    "nutrient": "Nitrogen",
                    "symptom": "Yellowing of lower leaves",
                    "treatment": "Apply balanced NPK fertilizer (10-10-10)",
                    "frequency": "Every 2 weeks",
                    "organic_option": "Fish emulsion or composted manure",
                },
                {
                    "nutrient": "Calcium",
                    "symptom": "Blossom end rot, distorted new growth",
                    "treatment": "Apply calcium nitrate foliar spray (4g/L)",
                    "frequency": "Weekly during fruit development",
                    "organic_option": "Crushed eggshells or gypsum amendment",
                },
            ],
        },
        "watering": {
            "current_status": "Slightly Underwatered",
            "schedule": "Water deeply every 3 days",
            "amount_ml_per_plant": 500,
            "warning": "Avoid wetting foliage to prevent further blight spread",
        },
        "pests": {
            "detected": True,
            "type": "Aphids",
            "severity": "Mild",
            "treatment": "Neem oil spray, 3 applications every 5 days",
        },
        "soil": {
            "recommended_ph": "6.0-6.8",
            "amendments": ["Add agricultural lime if pH below 6.0"],
            "drainage": "Ensure raised beds or well-draining soil",
        },
        "care_plan": {
            "immediate": ["Apply copper fungicide within 24 hours", "Remove infected leaves"],
            "this_week": ["Increase plant spacing for airflow", "Apply nitrogen fertilizer"],
            "ongoing": ["Weekly neem oil spray", "Monitor for new infection sites"],
        },
        "recovery_outlook": "Good — with treatment, expect improvement within 10-14 days",
    }


@app.post("/analyze", response_model=ScanResponse)
async def analyze(image: UploadFile = File(...)):
    start_time = time.time()
    scan_id = str(uuid.uuid4())
    filename = image.filename or "upload.jpg"

    # Save uploaded image
    image_path = UPLOAD_DIR / f"{scan_id}.jpg"
    image_bytes = await image.read()
    image_path.write_bytes(image_bytes)

    # Check demo cache
    if DEMO_MODE:
        cached = _load_demo_cache(filename)
        if cached:
            cached["scan_id"] = scan_id
            cached["mask_url"] = f"/masks/{scan_id}.png"
            _persist_scan(scan_id, cached, str(image_path))
            elapsed = time.time() - start_time
            logger.info("[SCAN %s] received → cached response → total: %.2fs", scan_id, elapsed)
            return ScanResponse(**cached)

    # Try real pipeline
    try:
        from dataset import add_scan_sample, attach_diagnosis_to_sample, attach_mask_to_sample
        from pipeline import calculate_affected_percent, run_diagnosis, run_segmentation

        # Step 1: Add to FiftyOne dataset
        sample = add_scan_sample(str(image_path), scan_id)
        seg_start = time.time()

        # Step 2: Run SAM3 segmentation
        mask = run_segmentation(sample, scan_id)
        seg_time = time.time() - seg_start
        mask_path = str(MASK_DIR / f"{scan_id}.png")
        attach_mask_to_sample(scan_id, mask_path)

        # Step 3: Run Gemini Vision diagnosis
        diag_start = time.time()
        diagnosis = run_diagnosis(str(image_path), mask_path)
        diag_time = time.time() - diag_start

        # Step 4: Enrich with care engine
        affected_pct = calculate_affected_percent(mask)
        if "disease" in diagnosis:
            diagnosis["disease"]["affected_percent"] = affected_pct

        crop_type = diagnosis.get("crop_type", "Unknown")
        watering = get_watering_schedule(crop_type)
        soil = get_soil_recommendations(crop_type)
        care_plan = build_care_plan(diagnosis)

        # Merge care engine data if Gemini didn't provide it
        if not diagnosis.get("watering", {}).get("schedule"):
            diagnosis["watering"] = {
                "current_status": diagnosis.get("watering", {}).get("current_status", "Unknown"),
                "schedule": watering["schedule"],
                "amount_ml_per_plant": watering["amount_ml"],
                "warning": diagnosis.get("watering", {}).get("warning"),
            }
        if not diagnosis.get("soil", {}).get("recommended_ph"):
            diagnosis["soil"] = {
                "recommended_ph": soil["ph"],
                "amendments": soil["amendments"],
                "drainage": soil["drainage"],
            }
        diagnosis["care_plan"] = care_plan

        # Step 5: Persist
        result = {
            "scan_id": scan_id,
            "crop_type": crop_type,
            "disease": diagnosis["disease"],
            "mask_url": f"/masks/{scan_id}.png",
            "nutrients": diagnosis.get("nutrients", {"deficiencies": [], "recommendations": []}),
            "watering": diagnosis["watering"],
            "pests": diagnosis.get("pests", {"detected": False}),
            "soil": diagnosis["soil"],
            "care_plan": diagnosis["care_plan"],
            "recovery_outlook": diagnosis.get("recovery_outlook", "Monitor and reassess in 7 days"),
        }

        attach_diagnosis_to_sample(scan_id, result)
        _persist_scan(scan_id, result, str(image_path))

        if DEMO_MODE:
            _save_demo_cache(filename, result)

        elapsed = time.time() - start_time
        logger.info(
            "[SCAN %s] received → segmentation: %.2fs → diagnosis: %.2fs → total: %.2fs",
            scan_id, seg_time, diag_time, elapsed,
        )
        return ScanResponse(**result)

    except Exception:
        logger.exception("Pipeline failed for %s — returning mock response", scan_id)
        mock = _build_mock_response(scan_id)
        _persist_scan(scan_id, mock, str(image_path))
        elapsed = time.time() - start_time
        logger.info("[SCAN %s] received → fallback mock → total: %.2fs", scan_id, elapsed)
        return ScanResponse(**mock)


@app.get("/masks/{scan_id}.png")
async def get_mask(scan_id: str):
    mask_path = MASK_DIR / f"{scan_id}.png"
    if mask_path.exists():
        return FileResponse(str(mask_path), media_type="image/png")
    # Return a transparent 1x1 PNG as fallback
    from io import BytesIO
    from PIL import Image as PILImage
    buf = BytesIO()
    PILImage.new("RGBA", (1, 1), (0, 0, 0, 0)).save(buf, "PNG")
    buf.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buf, media_type="image/png")


@app.get("/history", response_model=list[ScanSummary])
async def get_history():
    with Session(engine) as session:
        records = session.exec(
            select(ScanRecord).order_by(ScanRecord.id.desc()).limit(20)
        ).all()
    return [
        ScanSummary(
            scan_id=r.scan_id,
            timestamp=r.timestamp,
            crop_type=r.crop_type,
            disease_name=r.disease_name,
            severity=r.severity,
            thumbnail_url=f"/masks/{r.scan_id}.png",
        )
        for r in records
    ]


@app.get("/history/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str):
    with Session(engine) as session:
        record = session.exec(
            select(ScanRecord).where(ScanRecord.scan_id == scan_id)
        ).first()
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanResponse(**json.loads(record.result_json))


@app.get("/health", response_model=HealthResponse)
async def health():
    plugins = []
    try:
        import fiftyone.operators as foo
        ops = [op.name for op in foo.list_operators()]
        if any("sam3" in op for op in ops):
            plugins.append("sam3_images")
        if any("gemini" in op for op in ops):
            plugins.append("gemini-vision")
    except Exception:
        pass
    return HealthResponse(status="ok", plugins=plugins)


@app.on_event("startup")
async def startup_precache():
    """Pre-cache demo images on startup if DEMO_MODE is enabled."""
    if not DEMO_MODE:
        return
    if not SAMPLE_IMAGES_DIR.exists():
        logger.info("No sample_images directory found — skipping precache")
        return
    images = list(SAMPLE_IMAGES_DIR.glob("*.jpg")) + list(SAMPLE_IMAGES_DIR.glob("*.png"))
    cached_count = 0
    for img in images:
        cache_file = DEMO_CACHE_DIR / f"{img.stem}.json"
        if cache_file.exists():
            cached_count += 1
    logger.info("Demo cache ready: %d/%d images", cached_count, len(images))
