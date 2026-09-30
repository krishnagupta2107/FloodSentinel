# Flood Sentinels - Storm Drain Blockage Detection

An AI-powered flood prevention system that uses **YOLOv8 object detection** to identify sewage blockages and defects in storm drain CCTV footage, enabling early intervention before flood events occur.

---

## 🌍 Project Overview

Dense urban centers frequently experience sudden, severe flash flooding during heavy monsoon rains, often caused by unobserved trash and debris blockages in underground storm drainage networks. Current municipal drainage inspection is largely manual and reactive.

**Flood Sentinels** is an AI-powered urban drainage blockage detection and flash-flood early warning platform. It acts as a proactive decision-support system that unifies computer vision, sensor data, and geographic information to prioritize drainage maintenance *before* flooding occurs.

### 🚀 Key Modules (Full Pipeline)
1. **Debris & Blockage Detection (Computer Vision)**
   - Utilizes a fine-tuned **YOLOv8** model to process street-level or CCTV imagery of catch basins.
   - Detects the presence of sewage blockages and calculates the **Occlusion Percentage** (severity) of the drain grate.
   
2. **Overflow-Risk Prediction (Time-Series & Sensors)**
   - Fuses environmental data (public rainfall time-series) with underground water-level sensor telemetry.
   - Uses predictive machine learning to estimate the likelihood and timeframe of a drain overflow ahead of the observed rise.

3. **Risk Scoring & Prioritisation Module**
   - Synthesizes the visual blockage severity (from the CV model) and the predicted overflow risk (from the sensor model) alongside location vulnerability data.
   - Generates a ranked, unified **Risk Score (0-1)** for multiple drainage sites.

4. **Map-Based Alert Dashboard**
   - A frontend interface designed for municipal maintenance supervisors and emergency response coordinators.
   - Visualizes all monitored catch basins on an interactive map, color-coded by risk level, allowing crews to dispatch resources to the most critical locations first.

---

## 🧠 Detection Model Specs

| Property | Detail |
|----------|--------|
| **Task** | Object Detection (Sewage Blockage / Defects) |
| **Model** | YOLOv8 Nano (`yolov8n.pt`) |
| **Framework** | Ultralytics YOLOv8 |
| **Dataset** | Storm Drain CCTV footage (Roboflow annotated) |
| **GPU** | NVIDIA GeForce RTX 3050 6GB |

---

## Model Performance (flood_sentinels_v2 - 20 epochs)

| Split | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|-------|-----------|--------|---------|--------------|
| Validation | 0.602 | 0.679 | **0.685** | 0.435 |
| Test (unseen) | 0.631 | 0.680 | **0.685** | 0.387 |

- **Class detected:** Sewage blockage
- **Training time:** ~3.5 minutes (20 epochs)
- **Model size:** 6.2 MB

---

## Project Structure

```
Flood Sentinels/
├── yolov8n.pt                         # YOLOv8 base model (pretrained)
├── COMMANDS.txt                       # All commands reference
├── scripts/
│   ├── coco_to_yolo.py               # Converts COCO JSON labels to YOLO format
│   ├── estimate_occlusion.py         # Estimates blockage occlusion percentage
│   ├── plot_results.py               # Generates training loss & accuracy graphs
│   ├── sample_grid.py                # Creates visual grid of predictions
│   └── test_occlusion_batch.py       # Batch tests occlusion on test dataset
├── Yolo Dataset/
│   ├── data.yaml                     # Dataset config (nc=2, classes)
│   ├── train/images/                 # Training images
│   ├── train/labels/                 # YOLO format label files
│   ├── valid/images/                 # Validation images
│   ├── valid/labels/
│   ├── test/images/                  # Test images (unseen)
│   └── test/labels/
└── runs/detect/
    └── flood_sentinels_v2/
        ├── weights/
        │   ├── best.pt               # Best trained model
        │   └── last.pt               # Last epoch checkpoint
        ├── results.csv               # Per-epoch metrics
        ├── loss_curves.png           # Training loss visualization
        ├── accuracy_metrics.png      # mAP, Precision, Recall curves
        └── training_dashboard.png    # Full training dashboard
```

---

## Setup

### Requirements
- Python 3.10+
- CUDA-capable GPU (tested on RTX 3050)
- PyTorch with CUDA support

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/krishnagupta2107/FloodSentinel.git
cd FloodSentinel

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install PyTorch with CUDA (CUDA 12.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# 4. Install Ultralytics and dependencies
pip install ultralytics pandas matplotlib
```

---

## Usage

### 1. Prepare Dataset Labels (one-time)
```bash
python scripts/coco_to_yolo.py
```

### 2. Train the Model
```bash
yolo detect train data="Yolo Dataset/data.yaml" model=yolov8n.pt epochs=50 imgsz=640 batch=16 device=0 project=runs/detect name=flood_sentinels_v1 patience=15
```

### 3. Validate
```bash
yolo detect val model=runs/detect/flood_sentinels_v2/weights/best.pt data="Yolo Dataset/data.yaml" device=0 split=val
```

### 4. Test on Unseen Data
```bash
yolo detect val model=runs/detect/flood_sentinels_v2/weights/best.pt data="Yolo Dataset/data.yaml" device=0 split=test
```

### 5. Run Inference on Images/Video
```bash
# On images
yolo detect predict model=runs/detect/flood_sentinels_v2/weights/best.pt source="path/to/images" device=0 save=True conf=0.25

# On video
yolo detect predict model=runs/detect/flood_sentinels_v2/weights/best.pt source="path/to/video.mp4" device=0 save=True conf=0.25
```

### 6. Generate Training Graphs
```bash
python scripts/plot_results.py
```

### 7. Estimate Blockage Occlusion
```bash
# On a single image
python scripts/estimate_occlusion.py "path/to/image.jpg"

# Batch test on all test images
python scripts/test_occlusion_batch.py
```

---

## Dataset

- **Source:** Roboflow (storm drain CCTV footage)
- **Annotation format:** COCO JSON (converted to YOLO .txt)
- **Classes:** `Defects` (0), `Sewage blockage` (1)
- **Split:** 703 train / 198 valid / 98 test images

---

## Training Results

Training graphs are saved to `runs/detect/flood_sentinels_v2/`:

- `loss_curves.png` - Box, Classification & DFL loss (Train vs Val)
- `accuracy_metrics.png` - mAP@0.5, Precision, Recall over epochs
- `training_dashboard.png` - Full dark-theme summary dashboard

---

## References

- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com)
- [Roboflow Dataset](https://app.roboflow.com/krishna-gupta-v9ctt/storm-drain-model-cjhye-3oypn/1)

---

## License

CC BY 4.0 - Dataset license from Roboflow