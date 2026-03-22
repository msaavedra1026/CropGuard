#!/usr/bin/env python3
"""
CropGuard: Main pipeline for crop disease detection and visualization.

Usage:
    python cropguard.py                    # Run full pipeline
    python cropguard.py --step load        # Just load dataset
    python cropguard.py --step predict     # Run CLIP predictions
    python cropguard.py --step embeddings  # Compute embeddings
    python cropguard.py --step evaluate    # Evaluate predictions
    python cropguard.py --step app         # Launch FiftyOne App
    python cropguard.py --samples 500      # Limit sample count
"""

import argparse
import sys

# ── Pre-flight dependency check ───────────────────────────────────────────────
_missing = []
for pkg, imp in [("fiftyone", "fiftyone"), ("torch", "torch"), ("transformers", "transformers")]:
    try:
        __import__(imp)
    except ImportError:
        _missing.append(pkg)
if _missing:
    print(f"\nMissing required packages: {', '.join(_missing)}")
    print(f"Run: pip install {' '.join(_missing)}")
    print(f"Or run: python setup_check.py  for full diagnostics\n")
    sys.exit(1)

import fiftyone as fo


def main():
    parser = argparse.ArgumentParser(description="CropGuard: Crop Disease Detection Pipeline")
    parser.add_argument(
        "--step",
        choices=["load", "predict", "embeddings", "evaluate", "app", "all"],
        default="all",
        help="Which pipeline step to run (default: all)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=2000,
        help="Max samples to load (default: 2000, use 0 for all)",
    )
    parser.add_argument(
        "--dataset-name",
        default="cropguard",
        help="FiftyOne dataset name (default: cropguard)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5151,
        help="Port for FiftyOne App (default: 5151)",
    )
    args = parser.parse_args()

    max_samples = args.samples if args.samples > 0 else None
    dataset_name = args.dataset_name
    run_all = args.step == "all"

    print(r"""
   ╔═══════════════════════════════════════════╗
   ║         CropGuard v1.0                    ║
   ║   Crop Disease Detection with FiftyOne    ║
   ║         ASU Hackathon 2026                ║
   ╚═══════════════════════════════════════════╝
    """)

    # ── Step 1: Load Dataset ──────────────────────────────────────────────
    if run_all or args.step == "load":
        print("\n[1/4] Loading dataset...")
        from load_dataset import load_from_huggingface

        dataset = load_from_huggingface(
            max_samples=max_samples,
            dataset_name=dataset_name,
        )
        print(f"  Dataset: {len(dataset)} samples")
        print(f"  Classes: {len(dataset.distinct('ground_truth.label'))}")
        print(f"  Crops:   {dataset.distinct('crop_type')}")
    else:
        dataset = fo.load_dataset(dataset_name)
        print(f"Loaded existing dataset: {len(dataset)} samples")

    # ── Step 2: Run CLIP Predictions ──────────────────────────────────────
    if run_all or args.step == "predict":
        print("\n[2/4] Running CLIP zero-shot classification...")
        from predict import run_clip_predictions

        run_clip_predictions(dataset)

        # Quick preview
        print(f"\n  Sample predictions:")
        for sample in dataset.take(5):
            gt = sample.ground_truth.label if sample.ground_truth else "N/A"
            pred = sample.predictions.label if sample.predictions else "N/A"
            conf = sample.predictions.confidence if sample.predictions else 0
            match = "correct" if gt == pred else "WRONG"
            print(f"    GT: {gt[:35]:35s}  Pred: {pred[:35]:35s}  ({conf:.0%}) [{match}]")

    # ── Step 3: Compute Embeddings ────────────────────────────────────────
    if run_all or args.step == "embeddings":
        print("\n[3/4] Computing embeddings...")
        from embeddings import compute_embeddings

        compute_embeddings(dataset)

    # ── Step 4: Evaluate ──────────────────────────────────────────────────
    if run_all or args.step == "evaluate":
        print("\n[4/4] Evaluating predictions...")
        from evaluate import evaluate_predictions

        eval_results = evaluate_predictions(dataset)

    # ── Launch FiftyOne App ───────────────────────────────────────────────
    if run_all or args.step == "app":
        print(f"\nLaunching FiftyOne App on port {args.port}...")
        print(f"Open http://localhost:{args.port} in your browser")
        print("\nUseful things to try in the app:")
        print("  - Use the sidebar to filter by 'crop_type' or 'severity'")
        print("  - Open the 'Embeddings' panel to see disease clusters")
        print("  - Switch to saved views: 'misclassified', 'confident_mistakes'")
        print("  - Click any sample to see ground truth vs prediction")
        print("  - Sort by 'predictions.confidence' to find uncertain predictions")
        print("\nPress Ctrl+C to stop.\n")

        session = fo.launch_app(dataset, port=args.port)

        # Configure the app with useful defaults
        try:
            session.color_scheme = fo.ColorScheme(
                color_by="value",
                fields=[
                    fo.ColorSchemeField(
                        path="severity",
                        value_colors=[
                            fo.ValueColor(value="none", color="#22C55E"),
                            fo.ValueColor(value="moderate", color="#F59E0B"),
                            fo.ValueColor(value="high", color="#EF4444"),
                            fo.ValueColor(value="critical", color="#7C3AED"),
                        ],
                    )
                ],
            )
        except Exception:
            pass  # Color scheme config may not be available in all versions

        session.wait()


if __name__ == "__main__":
    main()
