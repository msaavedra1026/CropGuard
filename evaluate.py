"""
CropGuard: Evaluate model predictions using FiftyOne's evaluation framework.

Generates:
  - Per-class accuracy metrics
  - Confusion matrix
  - Misclassification analysis views
  - Confidence calibration insights
"""

import fiftyone as fo
from fiftyone import ViewField as F

from utils import DISEASE_CLASSES, parse_class_name


def evaluate_predictions(dataset, pred_field="predictions", gt_field="ground_truth"):
    """
    Run FiftyOne's classification evaluation and create useful views.
    
    Args:
        dataset: FiftyOne dataset with ground truth and predictions
        pred_field: Field name containing predictions
        gt_field: Field name containing ground truth
    
    Returns:
        dict with evaluation results and useful views
    """
    print("Running evaluation...")

    # ── Core evaluation ───────────────────────────────────────────────────
    results = dataset.evaluate_classifications(
        pred_field,
        gt_field=gt_field,
        eval_key="eval",
        classes=DISEASE_CLASSES,
    )

    # Print summary
    print(f"\n{'='*60}")
    print(f"  CropGuard Evaluation Results")
    print(f"{'='*60}")

    # Overall metrics
    metrics = results.metrics()
    print(f"\n  Overall accuracy: {metrics.get('accuracy', 0):.1%}")
    print(f"  Macro precision:  {metrics.get('precision', 0):.3f}")
    print(f"  Macro recall:     {metrics.get('recall', 0):.3f}")
    print(f"  Macro F1:         {metrics.get('fscore', 0):.3f}")

    # ── Per-crop analysis ─────────────────────────────────────────────────
    print(f"\n  Per-crop accuracy:")
    crop_stats = {}
    for cls in dataset.distinct(f"{gt_field}.label"):
        if cls is None:
            continue
        crop, disease = parse_class_name(cls)

        # Get samples for this class
        class_view = dataset.match(F(f"{gt_field}.label") == cls)
        correct_view = class_view.match(F(f"{pred_field}.label") == F(f"{gt_field}.label"))

        total = len(class_view)
        correct = len(correct_view)
        acc = correct / total if total > 0 else 0

        if crop not in crop_stats:
            crop_stats[crop] = {"correct": 0, "total": 0}
        crop_stats[crop]["correct"] += correct
        crop_stats[crop]["total"] += total

    for crop, stats in sorted(crop_stats.items()):
        acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        bar = "█" * int(acc * 20) + "░" * (20 - int(acc * 20))
        print(f"    {crop:20s} {bar} {acc:.1%} ({stats['correct']}/{stats['total']})")

    # ── Create useful views ───────────────────────────────────────────────
    views = {}

    # Misclassified samples
    views["misclassified"] = dataset.match(
        F(f"{pred_field}.label") != F(f"{gt_field}.label")
    )
    print(f"\n  Misclassified samples: {len(views['misclassified'])}")

    # High-confidence mistakes (most interesting for debugging)
    views["confident_mistakes"] = (
        dataset
        .match(F(f"{pred_field}.label") != F(f"{gt_field}.label"))
        .match(F(f"{pred_field}.confidence") > 0.5)
        .sort_by(f"{pred_field}.confidence", reverse=True)
    )
    print(f"  High-confidence mistakes: {len(views['confident_mistakes'])}")

    # Low-confidence correct (model is unsure but right)
    views["uncertain_correct"] = (
        dataset
        .match(F(f"{pred_field}.label") == F(f"{gt_field}.label"))
        .match(F(f"{pred_field}.confidence") < 0.4)
        .sort_by(f"{pred_field}.confidence")
    )
    print(f"  Low-confidence correct: {len(views['uncertain_correct'])}")

    # Critical severity misses (missed critical diseases)
    views["missed_critical"] = (
        dataset
        .match(F("severity") == "critical")
        .match(F(f"{pred_field}.label") != F(f"{gt_field}.label"))
    )
    print(f"  Missed critical diseases: {len(views['missed_critical'])}")

    # Healthy misclassified as diseased (false alarms)
    views["false_alarms"] = (
        dataset
        .match(F("is_healthy") == True)
        .match(F(f"{pred_field}.label") != F(f"{gt_field}.label"))
    )
    print(f"  False alarms (healthy -> diseased): {len(views['false_alarms'])}")

    # Diseased misclassified as healthy (missed diseases)
    views["missed_diseases"] = (
        dataset
        .match(F("is_healthy") == False)
        .match(F(f"eval") == "mistake")
    )

    # ── Save views to dataset ─────────────────────────────────────────────
    for name, view in views.items():
        try:
            dataset.save_view(name, view)
            print(f"  Saved view: '{name}'")
        except Exception:
            pass  # View might already exist

    print(f"\n{'='*60}")
    print(f"  Open FiftyOne App to explore these views!")
    print(f"{'='*60}\n")

    return {"results": results, "views": views, "metrics": metrics}


def print_confusion_matrix(dataset, results, top_n=10):
    """Print the most confused class pairs."""
    print(f"\nTop {top_n} most confused class pairs:")
    print(f"{'True Label':40s} {'Predicted':40s} {'Count':>6s}")
    print("-" * 90)

    try:
        cm = results.confusion_matrix()
        classes = results.classes

        # Find top confused pairs (off-diagonal)
        confused = []
        for i, true_cls in enumerate(classes):
            for j, pred_cls in enumerate(classes):
                if i != j and cm[i][j] > 0:
                    confused.append((true_cls, pred_cls, cm[i][j]))

        confused.sort(key=lambda x: x[2], reverse=True)

        for true_cls, pred_cls, count in confused[:top_n]:
            true_crop, true_disease = parse_class_name(true_cls)
            pred_crop, pred_disease = parse_class_name(pred_cls)
            print(f"{true_crop} {true_disease:30s} {pred_crop} {pred_disease:30s} {count:6d}")

    except Exception as e:
        print(f"Could not generate confusion matrix: {e}")


if __name__ == "__main__":
    dataset = fo.load_dataset("cropguard")
    eval_results = evaluate_predictions(dataset)
    print_confusion_matrix(dataset, eval_results["results"])
