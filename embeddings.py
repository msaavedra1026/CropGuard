"""
CropGuard: Compute embeddings for visual similarity analysis.

Uses CLIP embeddings to enable:
  - Embedding visualization in FiftyOne App (scatter plot of disease clusters)
  - Similarity search (find visually similar diseased leaves)
  - Outlier detection (find unusual samples)
"""

import fiftyone as fo
import fiftyone.zoo as foz
import fiftyone.brain as fob


def compute_embeddings(dataset, model_name="clip-vit-base32-torch"):
    """
    Compute CLIP embeddings for all samples and create a visualization.
    
    Args:
        dataset: FiftyOne dataset
        model_name: Model to use from FiftyOne Model Zoo
    
    Returns:
        The dataset with embeddings computed
    """
    print(f"Computing embeddings for {len(dataset)} samples...")

    # ── Compute embeddings via FiftyOne Model Zoo ─────────────────────────
    try:
        model = foz.load_zoo_model(model_name)

        # Compute and store embeddings
        dataset.compute_embeddings(
            model,
            embeddings_field="clip_embeddings",
        )
        print("Embeddings computed and stored in 'clip_embeddings' field")

    except Exception as e:
        print(f"FiftyOne model zoo embedding failed ({e}), trying direct approach...")
        _compute_embeddings_direct(dataset)

    # ── Create 2D visualization for the FiftyOne App ──────────────────────
    try:
        print("Computing 2D visualization (UMAP projection)...")
        fob.compute_visualization(
            dataset,
            embeddings="clip_embeddings",
            brain_key="clip_viz",
            method="umap",
            num_dims=2,
        )
        print("Visualization computed. Open 'Embeddings' panel in FiftyOne App.")

    except Exception as e:
        print(f"UMAP visualization failed ({e}), trying t-SNE...")
        try:
            fob.compute_visualization(
                dataset,
                embeddings="clip_embeddings",
                brain_key="clip_viz",
                method="tsne",
                num_dims=2,
            )
            print("t-SNE visualization computed.")
        except Exception as e2:
            print(f"t-SNE also failed ({e2}). Embeddings are still stored.")
            print("You can compute visualization manually in the FiftyOne App.")

    # ── Compute similarity index for nearest-neighbor search ──────────────
    try:
        print("Computing similarity index...")
        fob.compute_similarity(
            dataset,
            embeddings="clip_embeddings",
            brain_key="clip_similarity",
        )
        print("Similarity index ready. Use dataset.sort_by_similarity() to search.")

    except Exception as e:
        print(f"Similarity index failed ({e}). Skipping.")

    return dataset


def _compute_embeddings_direct(dataset):
    """Compute embeddings directly using HuggingFace Transformers."""
    import torch
    import numpy as np
    from transformers import CLIPProcessor, CLIPModel
    from PIL import Image

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Computing embeddings with direct CLIP on {device}...")

    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    embeddings = []
    filepaths = []

    for sample in dataset.iter_samples(progress=True):
        try:
            image = Image.open(sample.filepath).convert("RGB")
            inputs = processor(images=image, return_tensors="pt").to(device)

            with torch.no_grad():
                features = model.get_image_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
                embedding = features.cpu().numpy().flatten()

            sample["clip_embeddings"] = embedding.tolist()
            sample.save()

        except Exception as e:
            print(f"  Error with {sample.filepath}: {e}")
            continue

    print(f"Embeddings stored in 'clip_embeddings' field")


def find_similar_diseases(dataset, sample_id, k=10):
    """
    Find the k most similar samples to a given sample.
    Useful for finding similar disease presentations.
    
    Args:
        dataset: FiftyOne dataset with similarity computed
        sample_id: ID of the query sample
        k: Number of similar samples to return
    
    Returns:
        FiftyOne DatasetView of similar samples
    """
    try:
        view = dataset.sort_by_similarity(sample_id, k=k, brain_key="clip_similarity")
        return view
    except Exception as e:
        print(f"Similarity search failed: {e}")
        return None


if __name__ == "__main__":
    dataset = fo.load_dataset("cropguard")
    compute_embeddings(dataset)
    print(f"\nEmbedding stats:")
    print(f"  Samples with embeddings: {dataset.count('clip_embeddings')}")
