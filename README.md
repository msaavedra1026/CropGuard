# CropGuard 🌿

**AI-powered crop disease detection and visualization using FiftyOne + CLIP**

Built at the ASU Hackathon with Voxel51.

## What it does

CropGuard loads the PlantVillage dataset (54K+ leaf images across 14 crop species and 38 disease classes) into FiftyOne, runs zero-shot classification using CLIP to predict diseases without any training, computes embeddings for visual similarity analysis, and launches an interactive FiftyOne App where you can explore results, filter by disease, view confusion matrices, and discover patterns in crop health data.

## Quick Start

### 1. Set up environment

FiftyOne requires **Python 3.9 - 3.12**. We strongly recommend using a virtual environment:

```bash
# Create and activate a virtual environment
python -m venv cropguard-env
source cropguard-env/bin/activate    # Linux/Mac
# cropguard-env\Scripts\activate     # Windows
```

If you hit install issues, run this first:
```bash
pip install --upgrade pip setuptools wheel build
```

### 2. Install dependencies

```bash
# Core: FiftyOne (this also installs MongoDB and the FiftyOne App)
pip install fiftyone

# ML: PyTorch + CLIP + HuggingFace datasets
pip install torch torchvision transformers datasets Pillow

# Optional but recommended for embedding visualization
pip install umap-learn
```

Verify FiftyOne installed correctly:
```bash
python -c "import fiftyone as fo; print(fo.__version__)"
```

### 3. Verify everything works

```bash
python setup_check.py
```

This checks Python version, all dependencies, FiftyOne's database, CLIP availability, and GPU status. Fix anything marked `[MISSING]` before proceeding.

### 4. Run the pipeline

```bash
# Full pipeline: load data, run inference, compute embeddings, launch app
python cropguard.py

# Or run individual steps:
python cropguard.py --step load       # Just load the dataset
python cropguard.py --step predict    # Run CLIP predictions
python cropguard.py --step embeddings # Compute embeddings
python cropguard.py --step evaluate   # Run evaluation
python cropguard.py --step app        # Launch FiftyOne App
```

### 5. Explore in FiftyOne App

The app launches at `http://localhost:5151`. From there you can:

- **Filter by disease**: Use the sidebar to filter samples by ground truth or predicted label
- **View confidence scores**: Sort by prediction confidence to find uncertain classifications
- **Embedding visualization**: Open the Embeddings panel to see how diseases cluster
- **Confusion analysis**: Find misclassifications and understand model failure modes
- **Tag interesting samples**: Mark samples for review or further analysis

## Project Structure

```
cropguard/
├── README.md
├── setup_check.py        # Verify all dependencies before running
├── cropguard.py          # Main pipeline script
├── load_dataset.py       # Dataset loading from HuggingFace
├── predict.py            # CLIP zero-shot classification
├── evaluate.py           # Model evaluation with FiftyOne
├── embeddings.py         # Embedding computation and visualization
├── utils.py              # Disease class mappings and helpers
└── demo_dashboard.html   # Standalone demo dashboard
```

## Disease Classes

The system detects 38 classes across 14 crops including:

- **Apple**: Scab, Black Rot, Cedar Apple Rust, Healthy
- **Corn**: Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy
- **Grape**: Black Rot, Black Measles, Leaf Blight, Healthy
- **Tomato**: Bacterial Spot, Early/Late Blight, Leaf Mold, Mosaic Virus, and more
- **Potato**: Early Blight, Late Blight, Healthy
- Plus: Peach, Pepper, Cherry, Strawberry, Soybean, Squash, Orange, Blueberry, Raspberry

## How CLIP Zero-Shot Works Here

Instead of training a model on crop images, we use OpenAI's CLIP model which understands both images and text. We describe each disease class as a text prompt (e.g., "a photo of a tomato leaf with bacterial spot disease") and CLIP matches images to the most similar description. This means:

- No training data needed
- No GPU training time
- Works on new disease classes by just adding text descriptions
- Surprisingly accurate for a zero-shot approach

## Team

Built at the ASU Hackathon with Voxel51
