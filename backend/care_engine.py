"""Static knowledge base for crop care recommendations."""

from __future__ import annotations

WATERING_SCHEDULES: dict[str, dict] = {
    "Tomato":  {"schedule": "Water deeply every 2-3 days", "amount_ml": 500},
    "Wheat":   {"schedule": "Water every 5-7 days during grain fill", "amount_ml": 300},
    "Maize":   {"schedule": "Water deeply every 3-4 days", "amount_ml": 600},
    "Potato":  {"schedule": "Water every 3-4 days, keep soil consistently moist", "amount_ml": 450},
    "Rice":    {"schedule": "Maintain 2-5 cm standing water during vegetative stage", "amount_ml": 800},
    "Pepper":  {"schedule": "Water every 2-3 days, avoid waterlogging", "amount_ml": 400},
    "Cassava": {"schedule": "Water weekly once established, drought tolerant", "amount_ml": 350},
}

NUTRIENT_TREATMENTS: dict[str, dict] = {
    "Nitrogen": {
        "symptom": "Yellowing of lower/older leaves",
        "treatment": "Apply balanced NPK fertilizer (10-10-10) at 200g per plant",
        "frequency": "Every 2 weeks during growing season",
        "organic_option": "Fish emulsion or composted manure side-dress",
    },
    "Phosphorus": {
        "symptom": "Purple or dark tint on leaves and stems",
        "treatment": "Apply superphosphate (0-20-0) at 100g per square meter",
        "frequency": "Once at planting, once at flowering",
        "organic_option": "Bone meal worked into top 5cm of soil",
    },
    "Potassium": {
        "symptom": "Brown scorching on leaf edges",
        "treatment": "Apply potassium sulfate at 150g per square meter",
        "frequency": "Every 3 weeks during fruiting",
        "organic_option": "Wood ash or kelp meal",
    },
    "Calcium": {
        "symptom": "Blossom end rot, distorted new growth",
        "treatment": "Apply calcium nitrate foliar spray (4g/L)",
        "frequency": "Weekly during fruit development",
        "organic_option": "Crusite lime or gypsum amendment",
    },
    "Magnesium": {
        "symptom": "Interveinal chlorosis on older leaves",
        "treatment": "Apply Epsom salt foliar spray (20g/L)",
        "frequency": "Every 2 weeks",
        "organic_option": "Dolomitic lime soil amendment",
    },
    "Iron": {
        "symptom": "Interveinal chlorosis on young leaves",
        "treatment": "Apply chelated iron (Fe-EDDHA) at 5g per plant",
        "frequency": "Monthly",
        "organic_option": "Compost tea with iron-rich amendments",
    },
}

PEST_TREATMENTS: dict[str, dict] = {
    "Aphids": {
        "treatment": "Neem oil spray (5ml/L), 3 applications every 5 days",
        "biological": "Release ladybugs or lacewings",
        "companion_plants": "Marigolds, nasturtiums, garlic",
    },
    "Whiteflies": {
        "treatment": "Yellow sticky traps + insecticidal soap spray",
        "biological": "Encarsia formosa parasitic wasps",
        "companion_plants": "Basil, marigolds",
    },
    "Spider Mites": {
        "treatment": "Miticide spray or neem oil, increase humidity",
        "biological": "Predatory mites (Phytoseiulus persimilis)",
        "companion_plants": "Dill, coriander",
    },
    "Caterpillars": {
        "treatment": "Bacillus thuringiensis (Bt) spray weekly",
        "biological": "Encourage birds, parasitic wasps",
        "companion_plants": "Dill, fennel, parsley",
    },
    "Thrips": {
        "treatment": "Spinosad spray every 7 days, blue sticky traps",
        "biological": "Predatory mites, minute pirate bugs",
        "companion_plants": "Garlic, chives",
    },
}

SOIL_RECOMMENDATIONS: dict[str, dict] = {
    "Tomato":  {"ph": "6.0-6.8", "amendments": ["Add lime if pH < 6.0", "Compost for organic matter"], "drainage": "Well-draining raised beds or loamy soil"},
    "Wheat":   {"ph": "6.0-7.0", "amendments": ["Sulfur if pH > 7.5", "Green manure cover crop"], "drainage": "Good drainage, avoid waterlogging"},
    "Maize":   {"ph": "5.8-7.0", "amendments": ["Lime for acidic soils", "Incorporate crop residues"], "drainage": "Well-draining, deep tillage if compacted"},
    "Potato":  {"ph": "5.0-6.0", "amendments": ["Sulfur to lower pH if needed", "Heavy compost"], "drainage": "Loose, well-draining sandy loam"},
    "Rice":    {"ph": "5.5-6.5", "amendments": ["Lime for very acidic paddies", "Green manure"], "drainage": "Puddled clay with controlled water level"},
    "Pepper":  {"ph": "6.0-6.8", "amendments": ["Balanced compost", "Calcium if blossom end rot"], "drainage": "Well-draining with consistent moisture"},
    "Cassava": {"ph": "5.5-6.5", "amendments": ["Minimal fertilizer needed", "Mulch for moisture"], "drainage": "Sandy loam, tolerates poor soils"},
}


def get_watering_schedule(crop_type: str) -> dict:
    return WATERING_SCHEDULES.get(crop_type, WATERING_SCHEDULES["Tomato"])


def get_nutrient_plan(deficiencies: list[str]) -> list[dict]:
    results = []
    for nutrient in deficiencies:
        info = NUTRIENT_TREATMENTS.get(nutrient)
        if info:
            results.append({"nutrient": nutrient, **info})
    return results


def get_pest_treatment(pest_type: str) -> dict:
    return PEST_TREATMENTS.get(pest_type, {
        "treatment": "Apply broad-spectrum organic insecticide",
        "biological": "Encourage natural predators",
        "companion_plants": "Marigolds, basil",
    })


def get_soil_recommendations(crop_type: str) -> dict:
    return SOIL_RECOMMENDATIONS.get(crop_type, SOIL_RECOMMENDATIONS["Tomato"])


def build_care_plan(diagnosis: dict) -> dict:
    """Build a full care plan from a diagnosis dict."""
    immediate = []
    this_week = []
    ongoing = []

    # Disease actions
    severity = diagnosis.get("disease", {}).get("severity", "Mild")
    disease_name = diagnosis.get("disease", {}).get("name", "Unknown")

    if severity in ("Severe", "Critical"):
        immediate.append(f"Apply fungicide for {disease_name} within 24 hours")
        immediate.append("Remove and destroy heavily infected leaves")
    elif severity == "Moderate":
        immediate.append(f"Apply treatment for {disease_name} today")
        immediate.append("Remove visibly infected leaves")
    else:
        this_week.append(f"Monitor {disease_name} progression")

    # Nutrient actions
    deficiencies = diagnosis.get("nutrients", {}).get("deficiencies", [])
    for nutrient in deficiencies:
        info = NUTRIENT_TREATMENTS.get(nutrient)
        if info:
            this_week.append(f"Apply {nutrient.lower()} treatment: {info['treatment']}")

    # Pest actions
    pests = diagnosis.get("pests", {})
    if pests.get("detected"):
        pest_type = pests.get("type", "Unknown")
        pest_info = get_pest_treatment(pest_type)
        this_week.append(f"Begin pest control: {pest_info['treatment']}")

    # Ongoing care
    crop_type = diagnosis.get("crop_type", "Tomato")
    watering = get_watering_schedule(crop_type)
    ongoing.append(f"Watering: {watering['schedule']}")
    ongoing.append("Weekly visual inspection for new symptoms")
    ongoing.append("Monitor soil moisture before each watering")

    return {
        "immediate": immediate or ["No urgent actions needed"],
        "this_week": this_week or ["Continue regular care routine"],
        "ongoing": ongoing,
    }
