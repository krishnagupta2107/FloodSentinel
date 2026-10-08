# Flood Sentinel - Storm Drain Blockage Detection

An AI-powered system that uses **YOLOv8 object detection** to identify sewage blockages and defects in storm drain CCTV footage, along with an upcoming **LSTM/XGBoost** model for overflow-risk prediction.

---

## 🌍 Project Overview

Dense urban centers frequently experience sudden, severe flash flooding during heavy monsoon rains, often caused by unobserved trash and debris blockages in underground storm drainage networks. Current municipal drainage inspection is largely manual and reactive.

**Flood Sentinel** is an AI-powered urban drainage blockage detection and flash-flood early warning platform.

### 🚀 Key Modules (Full Pipeline)
1. **Debris & Blockage Detection (Computer Vision)**
   - Utilizes a fine-tuned **YOLOv8** model to process street-level or CCTV imagery of catch basins.
   - Detects the presence of sewage blockages and defects, outputting bounding boxes.
   
2. **Overflow-Risk Prediction (Time-Series & Sensors)**
   - **(Upcoming)** A predictive machine learning model utilizing **LSTM** (Long Short-Term Memory) and **XGBoost** to estimate overflow risk based on sensor telemetry and rainfall data.

3. **Map-Based Alert Dashboard**
   - **(Planned)** A frontend interface to visualize monitored catch basins on an interactive map.

---

## 🧠 Detection Model Specs

| Property | Detail |
|----------|--------|
| **Task** | Object Detection (Defects / Sewage blockage) |
| **Model** | YOLOv8 Nano (`yolov8n.pt`) |
| **Framework** | Ultralytics YOLOv8 |
| **Dataset** | Storm Drain CCTV footage (Roboflow annotated, 999 images) |
| **GPU** | NVIDIA GeForce RTX 3050 6GB |

---

## Model Performance 

### Vision Model (`flood_sentinels_v3` - 50 epochs)

| Metric | Score |
|--------|-------|
| mAP@0.5 (final) | 0.689 (best 0.705, ep. 46) |
| mAP@0.5:0.95 (final) | 0.430 |

*(Note: Per-class metrics for Defects vs. Sewage blockage are available in the evaluation run results.)*

### Model 3: Rainfall Forecasting

The rainfall forecasting component utilizes **XGBoost** and **LSTM** architectures to predict next-month rainfall based on a 12-month historical rainfall lookback window evaluated on a chronological train/test split.

> **Note:** The current implementation represents the rainfall forecasting component and should not be described as the complete rainfall + water-level overflow-risk system in the absence of real-time water-level telemetry sensors.

#### Evaluation Results (Chronological Test Set)

| Model | MAE (mm) | RMSE (mm) | R² |
|---|---|---|---|
| **XGBoost** | **43.7539** | **74.5815** | **0.8036** |
| **LSTM** | 49.1260 | 79.7615 | 0.7753 |

*XGBoost performed better on the current test set across MAE, RMSE, and R².*

- **Prediction Module:** `src/floodsentinel/models/rainfall_predictor.py`
- **Evaluation Module:** `src/floodsentinel/models/evaluate_rainfall.py`

---

## Limitations & Data Provenance

- **Vision Data:** The dataset consists of 999 CCTV images (703 train, 198 valid, 98 test). Data is sourced from Roboflow under CC BY 4.0. Due to potential frame extraction from video, there may be data leakage across splits.

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

# 3. Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## Usage

### 1. Prepare Dataset Labels (one-time)
```bash
python src/floodsentinel/coco_to_yolo.py
```

### 2. Train the Model (Config-based)
```bash
# Use train.py once implemented, or use the YOLO CLI:
yolo detect train data="Yolo Dataset/data.yaml" model=yolov8n.pt epochs=50 imgsz=640 batch=16 device=0 project=runs/detect name=flood_sentinels_v3 patience=15
```

### 3. Estimate Blockage Occlusion
```bash
# On a single image
python src/floodsentinel/estimate_occlusion.py "path/to/image.jpg"

# Batch test on all test images
python src/floodsentinel/batch_inference.py
```

### 4. Run Rainfall Forecasting Evaluation
```bash
python3 -m src.floodsentinel.models.evaluate_rainfall
```

---

## License

Code is licensed under the MIT License.
Dataset is licensed under CC BY 4.0 (Roboflow).