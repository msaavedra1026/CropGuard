#!/usr/bin/env python3
"""
CropGuard: Setup verification script.
Run this first to check that all dependencies are installed correctly.

Usage:
    python setup_check.py
"""

import sys
import subprocess


def check(name, import_name=None, min_version=None):
    """Check if a package is importable and optionally verify version."""
    import_name = import_name or name
    try:
        mod = __import__(import_name)
        version = getattr(mod, "__version__", "unknown")
        print(f"  [OK]  {name:20s} v{version}")
        return True
    except ImportError:
        print(f"  [MISSING] {name:20s} --> pip install {name}")
        return False


def main():
    print("=" * 55)
    print("  CropGuard Setup Check")
    print("=" * 55)

    # Python version
    v = sys.version_info
    py_ok = (3, 9) <= (v.major, v.minor) <= (3, 12)
    status = "OK" if py_ok else "WRONG VERSION"
    print(f"\n  Python {v.major}.{v.minor}.{v.micro} [{status}]")
    if not py_ok:
        print(f"  FiftyOne requires Python 3.9-3.12.")
        print(f"  You have Python {v.major}.{v.minor}.")

    # Check virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    print(f"  Virtual environment: {'Yes' if in_venv else 'No (recommended!)'}")

    print(f"\n  Core packages:")
    all_ok = True
    all_ok &= check("fiftyone", "fiftyone")
    all_ok &= check("torch", "torch")
    all_ok &= check("torchvision", "torchvision")
    all_ok &= check("transformers", "transformers")
    all_ok &= check("datasets", "datasets")
    all_ok &= check("Pillow", "PIL")

    print(f"\n  Optional packages:")
    check("umap-learn", "umap")
    check("ipython", "IPython")

    # Check FiftyOne can start its database
    print(f"\n  FiftyOne database check:")
    try:
        import fiftyone as fo
        # This triggers the MongoDB connection
        fo.list_datasets()
        print(f"  [OK]  FiftyOne database is running")
    except Exception as e:
        print(f"  [WARN] Database issue: {e}")
        print(f"         This usually resolves on first run.")
        print(f"         If 'Could not find mongod', see:")
        print(f"         https://docs.voxel51.com/getting_started/install.html")

    # Check CLIP model availability
    print(f"\n  CLIP model check:")
    try:
        from transformers import CLIPProcessor, CLIPModel
        print(f"  [OK]  CLIP classes available")
        print(f"         Model will download on first run (~600MB)")
    except ImportError:
        print(f"  [MISSING] transformers CLIP support")
        all_ok = False

    # Check GPU
    print(f"\n  Hardware:")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"  [OK]  CUDA GPU: {gpu_name}")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            print(f"  [OK]  Apple MPS (Metal) available")
        else:
            print(f"  [INFO] CPU only (works fine, just slower)")
    except Exception:
        print(f"  [INFO] CPU only")

    # Summary
    print(f"\n{'=' * 55}")
    if all_ok:
        print(f"  All good! Run: python cropguard.py")
    else:
        print(f"  Some packages are missing. Install them and re-run.")
        print(f"\n  Quick fix:")
        print(f"  pip install --upgrade pip setuptools wheel build")
        print(f"  pip install fiftyone torch torchvision transformers datasets Pillow")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
