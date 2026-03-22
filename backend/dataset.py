"""FiftyOne dataset management for the cropguard dataset."""

from __future__ import annotations

import logging

import fiftyone as fo

logger = logging.getLogger(__name__)

DATASET_NAME = "cropguard"


def get_or_create_dataset() -> fo.Dataset:
    """Return the cropguard dataset, creating it if needed."""
    if fo.dataset_exists(DATASET_NAME):
        return fo.load_dataset(DATASET_NAME)
    dataset = fo.Dataset(DATASET_NAME, persistent=True)
    logger.info("Created new FiftyOne dataset: %s", DATASET_NAME)
    return dataset


def add_scan_sample(image_path: str, scan_id: str) -> fo.Sample:
    """Add an image to the dataset and tag it with the scan_id."""
    dataset = get_or_create_dataset()
    sample = fo.Sample(filepath=image_path)
    sample.tags.append(scan_id)
    sample["scan_id"] = scan_id
    dataset.add_sample(sample)
    logger.info("Added sample %s to dataset", scan_id)
    return sample


def attach_mask_to_sample(scan_id: str, mask_path: str) -> None:
    """Attach a segmentation mask PNG to the sample."""
    dataset = get_or_create_dataset()
    view = dataset.match_tags(scan_id)
    if len(view) == 0:
        logger.warning("No sample found for scan_id %s", scan_id)
        return
    sample = view.first()
    sample["segmentation_mask_path"] = mask_path
    sample.save()
    logger.info("Attached mask to sample %s", scan_id)


def attach_diagnosis_to_sample(scan_id: str, diagnosis_dict: dict) -> None:
    """Store the full diagnosis as custom fields on the sample."""
    dataset = get_or_create_dataset()
    view = dataset.match_tags(scan_id)
    if len(view) == 0:
        logger.warning("No sample found for scan_id %s", scan_id)
        return
    sample = view.first()
    disease = diagnosis_dict.get("disease", {})
    sample["disease_name"] = disease.get("name", "Unknown")
    sample["severity"] = disease.get("severity", "Unknown")
    sample["confidence"] = disease.get("confidence", 0.0)
    sample["crop_type"] = diagnosis_dict.get("crop_type", "Unknown")
    sample["diagnosis"] = diagnosis_dict
    sample.save()
    logger.info("Attached diagnosis to sample %s", scan_id)
