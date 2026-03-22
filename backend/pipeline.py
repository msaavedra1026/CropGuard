"""CV pipeline — SAM3 segmentation + Gemini Vision diagnosis."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import numpy as np
from PIL import Image

from care_engine import build_care_plan

logger = logging.getLogger(__name__)

MASK_DIR = Path("/tmp/cropguard/masks")
MASK_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_PROMPT = """You are an expert agronomist and plant pathologist with 20 years of field
experience. Analyze this crop image and provide a complete plant health
assessment.

Return ONLY valid JSON — no markdown, no backticks, no explanation text.
Use exactly these keys:

{
  "crop_type": "string — identified plant species",
  "disease": {
    "name": "string",
    "confidence": 0.0,
    "severity": "Mild | Moderate | Severe | Critical",
    "description": "string",
    "spread_risk": "Low | Medium | High"
  },
  "nutrients": {
    "deficiencies": ["string"],
    "recommendations": [{
      "nutrient": "string",
      "symptom": "string",
      "treatment": "string",
      "frequency": "string",
      "organic_option": "string"
    }]
  },
  "watering": {
    "current_status": "string",
    "schedule": "string",
    "amount_ml_per_plant": 0,
    "warning": "string or null"
  },
  "pests": {
    "detected": true,
    "type": "string or null",
    "severity": "string or null",
    "treatment": "string or null"
  },
  "soil": {
    "recommended_ph": "string",
    "amendments": ["string"],
    "drainage": "string"
  },
  "care_plan": {
    "immediate": ["string"],
    "this_week": ["string"],
    "ongoing": ["string"]
  },
  "recovery_outlook": "string"
}

Be specific, actionable, and farmer-friendly. Assume the farmer has access
to both local markets and agricultural suppliers."""


# ---------------------------------------------------------------------------
# Gemini Vision Diagnosis (using google.genai — the working library)
# ---------------------------------------------------------------------------

def run_diagnosis(image_path: str, mask_path: str = None) -> dict:
    """Run Gemini Vision diagnosis on the image and return parsed dict."""
    try:
        from google import genai

        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            logger.error("No GEMINI_API_KEY set")
            return _fallback_diagnosis(image_path)

        client = genai.Client(api_key=key)
        img = Image.open(image_path)

        # Build content parts
        parts = [GEMINI_PROMPT, img]
        if mask_path and Path(mask_path).exists():
            mask_img = Image.open(mask_path)
            parts.extend(["Segmentation mask of affected region:", mask_img])

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=parts,
        )

        raw_text = response.text.strip()

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        diagnosis = json.loads(raw_text)
        logger.info("Gemini diagnosis parsed successfully")
        return diagnosis

    except json.JSONDecodeError as exc:
        logger.exception("Gemini returned invalid JSON: %s", exc)
        return _fallback_diagnosis(image_path)
    except Exception as exc:
        logger.exception("Diagnosis failed: %s", exc)
        return _fallback_diagnosis(image_path)


# ---------------------------------------------------------------------------
# SAM3 Segmentation (Zoo Model approach)
# ---------------------------------------------------------------------------

def run_segmentation(sample, scan_id: str) -> np.ndarray | None:
    """Run SAM3 segmentation on a sample and return the mask."""
    try:
        import fiftyone.zoo as foz

        # Register the remote model source
        foz.register_zoo_model_source(
            "https://github.com/harpreetsahota204/sam3_images"
        )

        model = foz.load_zoo_model("facebook/sam3")
        model.operation = "automatic_segmentation"
        model.auto_kwargs = {
            "points_per_side": 16,
            "points_per_batch": 256,
            "quality_threshold": 0.7,
            "iou_threshold": 0.85,
            "max_masks": 50,
        }

        # Get the dataset this sample belongs to
        dataset = sample.dataset
        view = dataset.select(sample.id)
        view.apply_model(model, label_field="sam_segmentation", batch_size=1)

        # Reload sample
        sample.reload()

        # Export mask as PNG
        mask_path = MASK_DIR / f"{scan_id}.png"
        mask_array = _export_mask(sample, mask_path)
        return mask_array

    except Exception:
        logger.exception("Segmentation failed for %s", scan_id)
        return None


def _export_mask(sample, mask_path: Path) -> np.ndarray | None:
    """Export SAM3 detections as a combined binary mask PNG."""
    img = Image.open(sample.filepath)
    w, h = img.size
    combined = np.zeros((h, w), dtype=np.uint8)

    seg = sample.get_field("sam_segmentation")
    if not seg or not hasattr(seg, "detections") or not seg.detections:
        # Save empty mask
        Image.fromarray(combined).save(str(mask_path))
        return None

    for det in seg.detections:
        if det.mask is None:
            continue
        bx, by, bw, bh = det.bounding_box
        x1, y1 = int(bx * w), int(by * h)
        mw, mh = int(bw * w), int(bh * h)
        if mw <= 0 or mh <= 0:
            continue

        mask_resized = np.array(
            Image.fromarray(det.mask.astype(np.uint8) * 255).resize((mw, mh))
        )
        x2 = min(x1 + mw, w)
        y2 = min(y1 + mh, h)
        cw, ch = x2 - x1, y2 - y1
        combined[y1:y2, x1:x2] = np.maximum(
            combined[y1:y2, x1:x2], mask_resized[:ch, :cw]
        )

    Image.fromarray(combined).save(str(mask_path))
    return combined if np.any(combined) else None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def calculate_affected_percent(mask: np.ndarray | None) -> float:
    """Calculate percentage of image covered by mask."""
    if mask is None:
        return 0.0
    total_pixels = mask.size
    affected_pixels = np.count_nonzero(mask)
    return round((affected_pixels / total_pixels) * 100, 1)


def _fallback_diagnosis(image_path: str) -> dict:
    """Return a safe fallback so the app never crashes mid-demo."""
    return {
        "crop_type": "Unknown",
        "disease": {
            "name": "Analysis Unavailable",
            "confidence": 0.0,
            "severity": "Mild",
            "description": "Could not complete automated analysis. Manual inspection recommended.",
            "spread_risk": "Low",
        },
        "nutrients": {"deficiencies": [], "recommendations": []},
        "watering": {
            "current_status": "Unknown",
            "schedule": "Water as per standard crop guidelines",
            "amount_ml_per_plant": 500,
            "warning": None,
        },
        "pests": {"detected": False, "type": None, "severity": None, "treatment": None},
        "soil": {
            "recommended_ph": "6.0-7.0",
            "amendments": ["Test soil pH before amending"],
            "drainage": "Ensure adequate drainage",
        },
        "care_plan": build_care_plan({}),
        "recovery_outlook": "Manual inspection recommended for accurate assessment",
    }