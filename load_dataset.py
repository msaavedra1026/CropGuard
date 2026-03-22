"""
CropGuard: Load PlantVillage dataset into FiftyOne from HuggingFace.

Two loading strategies:
  1. Direct from HuggingFace Hub using FiftyOne's integration (preferred)
  2. Fallback: load via datasets library and manually create FiftyOne samples
"""

import os
import fiftyone as fo
from utils import DISEASE_CLASSES, parse_class_name, get_severity, DISPLAY_NAMES


def load_from_huggingface(max_samples=2000, dataset_name="cropguard"):
    """
    Load PlantVillage dataset from HuggingFace into FiftyOne.
    
    Uses the `datasets` library to pull images and labels, then
    creates a FiftyOne dataset with rich metadata.
    
    Args:
        max_samples: Number of samples to load (use None for all ~54K).
                     2000 is a good default for hackathon speed.
        dataset_name: Name for the FiftyOne dataset.
    
    Returns:
        fo.Dataset: The loaded FiftyOne dataset.
    """
    # Delete existing dataset with same name if it exists
    if fo.dataset_exists(dataset_name):
        fo.delete_dataset(dataset_name)

    print(f"Loading PlantVillage dataset (max {max_samples} samples)...")

    # ── Strategy 1: Try FiftyOne's native HuggingFace integration ─────────
    try:
        from fiftyone.utils.huggingface import load_from_hub

        dataset = load_from_hub(
            "mohanty/PlantVillage",
            format="parquet",
            classification_fields="label",
            max_samples=max_samples,
            name=dataset_name,
        )
        print(f"Loaded {len(dataset)} samples via FiftyOne HuggingFace integration")
        _enrich_dataset(dataset)
        return dataset

    except Exception as e:
        print(f"FiftyOne hub integration failed ({e}), falling back to datasets library...")

    # ── Strategy 2: Fallback via datasets library ─────────────────────────
    try:
        from datasets import load_dataset

        hf_dataset = load_dataset("mohanty/PlantVillage", "color", split="train")

        # Get label names
        label_names = hf_dataset.features["label"].names

        dataset = fo.Dataset(dataset_name)
        dataset.persistent = True

        samples = []
        save_dir = os.path.expanduser("~/cropguard_images")
        os.makedirs(save_dir, exist_ok=True)

        limit = max_samples if max_samples else len(hf_dataset)

        for i, item in enumerate(hf_dataset):
            if i >= limit:
                break

            # Save image to disk (FiftyOne needs file paths)
            label_name = label_names[item["label"]]
            img_path = os.path.join(save_dir, f"{label_name}_{i}.jpg")

            if not os.path.exists(img_path):
                item["image"].save(img_path)

            # Parse metadata
            crop, disease = parse_class_name(label_name)
            severity_info = get_severity(label_name)

            sample = fo.Sample(filepath=img_path)
            sample["ground_truth"] = fo.Classification(label=label_name)
            sample["crop_type"] = crop
            sample["disease_name"] = disease
            sample["display_name"] = DISPLAY_NAMES.get(label_name, label_name)
            sample["severity"] = severity_info["severity"]
            sample["recommended_action"] = severity_info["action"]
            sample["is_healthy"] = disease.lower() == "healthy"

            # Add train/test split tag
            sample.tags.append("train" if i % 5 != 0 else "test")

            samples.append(sample)

            if (i + 1) % 200 == 0:
                print(f"  Processed {i + 1}/{limit} samples...")

        dataset.add_samples(samples)
        print(f"Loaded {len(dataset)} samples via datasets library fallback")
        return dataset

    except Exception as e:
        print(f"Datasets library also failed: {e}")
        print("Creating a synthetic demo dataset instead...")
        return _create_demo_dataset(dataset_name)


def _enrich_dataset(dataset):
    """Add crop type, disease name, severity, and other metadata to samples."""
    print("Enriching dataset with metadata...")

    for sample in dataset.iter_samples(autosave=True, progress=True):
        if sample.ground_truth and sample.ground_truth.label:
            label = sample.ground_truth.label
            crop, disease = parse_class_name(label)
            severity_info = get_severity(label)

            sample["crop_type"] = crop
            sample["disease_name"] = disease
            sample["display_name"] = DISPLAY_NAMES.get(label, label)
            sample["severity"] = severity_info["severity"]
            sample["recommended_action"] = severity_info["action"]
            sample["is_healthy"] = disease.lower() == "healthy"


def _create_demo_dataset(dataset_name="cropguard"):
    """
    Create a small synthetic demo dataset if real data can't be loaded.
    Uses placeholder images so the FiftyOne App still works for the demo.
    """
    import numpy as np
    from PIL import Image

    print("Creating synthetic demo dataset...")

    if fo.dataset_exists(dataset_name):
        fo.delete_dataset(dataset_name)

    dataset = fo.Dataset(dataset_name)
    dataset.persistent = True

    save_dir = os.path.expanduser("~/cropguard_demo_images")
    os.makedirs(save_dir, exist_ok=True)

    samples = []
    # Create 10 samples per class for first 10 classes
    for cls in DISEASE_CLASSES[:10]:
        crop, disease = parse_class_name(cls)
        severity_info = get_severity(cls)

        for j in range(10):
            # Create a colored placeholder image
            if disease.lower() == "healthy":
                color = (34, 139, 34)  # Green for healthy
            else:
                color = (139, 69, 19)  # Brown for diseased
            
            img = Image.new("RGB", (256, 256), color)
            # Add some random variation
            arr = np.array(img)
            noise = np.random.randint(-30, 30, arr.shape, dtype=np.int16)
            arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)

            img_path = os.path.join(save_dir, f"{cls}_{j}.jpg")
            img.save(img_path)

            sample = fo.Sample(filepath=img_path)
            sample["ground_truth"] = fo.Classification(label=cls)
            sample["crop_type"] = crop
            sample["disease_name"] = disease
            sample["display_name"] = DISPLAY_NAMES.get(cls, cls)
            sample["severity"] = severity_info["severity"]
            sample["recommended_action"] = severity_info["action"]
            sample["is_healthy"] = disease.lower() == "healthy"
            sample.tags.append("train" if j < 8 else "test")

            samples.append(sample)

    dataset.add_samples(samples)
    print(f"Created demo dataset with {len(dataset)} synthetic samples")
    return dataset


if __name__ == "__main__":
    dataset = load_from_huggingface(max_samples=2000)
    print(f"\nDataset: {dataset}")
    print(f"Classes: {dataset.distinct('ground_truth.label')}")
    print(f"Crops: {dataset.distinct('crop_type')}")
    print(f"Severity levels: {dataset.distinct('severity')}")
