"""
CropGuard utilities: disease class mappings, CLIP prompt templates, and helpers.
"""

# ── Full PlantVillage class list ──────────────────────────────────────────────
# These map the folder/label names from PlantVillage to structured metadata

DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


def parse_class_name(class_name):
    """Parse a PlantVillage class name into crop and disease components."""
    parts = class_name.split("___")
    crop = parts[0].replace("_", " ").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "unknown"
    return crop, disease


def get_clip_prompt(class_name):
    """Generate a CLIP-friendly text prompt for a disease class."""
    crop, disease = parse_class_name(class_name)
    if disease.lower() == "healthy":
        return f"a photo of a healthy {crop} leaf"
    else:
        return f"a photo of a {crop} leaf with {disease}"


# Pre-built CLIP prompts for all classes
CLIP_PROMPTS = {cls: get_clip_prompt(cls) for cls in DISEASE_CLASSES}

# Human-readable display names
DISPLAY_NAMES = {}
for cls in DISEASE_CLASSES:
    crop, disease = parse_class_name(cls)
    if disease.lower() == "healthy":
        DISPLAY_NAMES[cls] = f"{crop} (Healthy)"
    else:
        DISPLAY_NAMES[cls] = f"{crop} - {disease}"


# ── Crop groupings for filtering ──────────────────────────────────────────────

CROPS = {}
for cls in DISEASE_CLASSES:
    crop, disease = parse_class_name(cls)
    if crop not in CROPS:
        CROPS[crop] = []
    CROPS[crop].append(cls)


# ── Severity metadata (for enriching the FiftyOne dataset) ────────────────────

SEVERITY_INFO = {
    "healthy": {"severity": "none", "action": "No action needed"},
    "Apple_scab": {"severity": "moderate", "action": "Apply fungicide, remove fallen leaves"},
    "Black_rot": {"severity": "high", "action": "Prune infected areas, apply copper spray"},
    "Cedar_apple_rust": {"severity": "moderate", "action": "Remove nearby juniper hosts"},
    "Powdery_mildew": {"severity": "moderate", "action": "Improve air circulation, apply sulfur"},
    "Cercospora_leaf_spot Gray_leaf_spot": {"severity": "high", "action": "Rotate crops, apply fungicide"},
    "Common_rust_": {"severity": "moderate", "action": "Plant resistant varieties"},
    "Northern_Leaf_Blight": {"severity": "high", "action": "Crop rotation, resistant hybrids"},
    "Esca_(Black_Measles)": {"severity": "high", "action": "Remove infected vines"},
    "Leaf_blight_(Isariopsis_Leaf_Spot)": {"severity": "moderate", "action": "Fungicide application"},
    "Haunglongbing_(Citrus_greening)": {"severity": "critical", "action": "Remove infected trees immediately"},
    "Bacterial_spot": {"severity": "high", "action": "Copper-based bactericide, remove debris"},
    "Early_blight": {"severity": "moderate", "action": "Fungicide, crop rotation"},
    "Late_blight": {"severity": "critical", "action": "Immediate fungicide, destroy infected plants"},
    "Leaf_Mold": {"severity": "moderate", "action": "Reduce humidity, improve ventilation"},
    "Septoria_leaf_spot": {"severity": "moderate", "action": "Remove lower leaves, apply fungicide"},
    "Spider_mites Two-spotted_spider_mite": {"severity": "moderate", "action": "Miticide application, introduce predatory mites"},
    "Target_Spot": {"severity": "moderate", "action": "Fungicide, proper spacing"},
    "Tomato_Yellow_Leaf_Curl_Virus": {"severity": "critical", "action": "Remove infected plants, control whitefly"},
    "Tomato_mosaic_virus": {"severity": "high", "action": "Remove infected plants, sanitize tools"},
    "Leaf_scorch": {"severity": "moderate", "action": "Improve watering, remove affected leaves"},
}


def get_severity(class_name):
    """Get severity info for a disease class."""
    _, disease = parse_class_name(class_name)
    # Try exact match first, then partial match
    if disease in SEVERITY_INFO:
        return SEVERITY_INFO[disease]
    for key, info in SEVERITY_INFO.items():
        if key.lower() in disease.lower() or disease.lower() in key.lower():
            return info
    return {"severity": "unknown", "action": "Consult agricultural extension service"}


if __name__ == "__main__":
    print(f"Total classes: {len(DISEASE_CLASSES)}")
    print(f"Crops: {list(CROPS.keys())}")
    print(f"\nSample CLIP prompts:")
    for cls in DISEASE_CLASSES[:5]:
        print(f"  {DISPLAY_NAMES[cls]}: \"{CLIP_PROMPTS[cls]}\"")
