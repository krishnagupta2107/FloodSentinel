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

| Model | MAE (mm) | RMSE (mm) | R² (Coeff. of Determination) |
|---|---|---|---|
| **XGBoost** | 43.6052 | 73.9722 | 0.8068 |
| **LSTM (Subdivision-Aware)** | 43.3720 | 70.4140 | 0.8249 |
| **XGBoost + LSTM Average** | **42.4741** | **70.4339** | **0.8248** |

*Both individual models and the ensemble exceed R² > 0.80 on the chronological test split.*

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

### 5. Run Multi-Modal Risk Fusion Demo
```bash
python scripts/demo_risk_fusion.py
```

---

## ⚡ Risk Fusion & Prioritisation

The **Risk Fusion & Prioritisation Module** synthesizes multimodal intelligence across visual inspections, sensor telemetry, and meteorological forecasts into a unified, actionable **Risk Score (0.0 to 1.0)** for ranking municipal catch basins.

### Pipeline Architecture

```text
CCTV Inspection / Grate Image
       ↓
YOLOv8 Detection & Occlusion Severity (0.0 - 1.0)
       ↓
Underground Sensor Telemetry → XGBoost 15m/30m Overflow Probability (0.0 - 1.0)
       ↓
Rainfall Time-Series → LSTM/XGBoost Forecast (mm) → Empirical Percentile Normalization (0.0 - 1.0)
       ↓
Optional Site Vulnerability (0.0 - 1.0)
       ↓
Unified Multi-Modal Risk Score (0.0 - 1.0)
       ↓
Priority-Ranked Drainage Sites (Rank #1 = Critical)
```

### Risk Score Formulation

The unified risk score is computed as a weighted linear combination of calibrated sub-scores:

$$\text{Risk Score} = w_{\text{blockage}} \cdot S_{\text{blockage}} + w_{\text{overflow}} \cdot S_{\text{overflow}} + w_{\text{rainfall}} \cdot S_{\text{rainfall}} + w_{\text{vulnerability}} \cdot S_{\text{vulnerability}}$$

where active weights dynamically re-normalize to $\sum w_i = 1.0$.

#### Configurable Components:
1. **Blockage Score ($S_{\text{blockage}}$):** Normalized CCTV grate visual occlusion:
   $$S_{\text{blockage}} = \text{clamp}\left(\frac{\text{occlusion\_percentage}}{100.0}, 0.0, 1.0\right)$$
2. **Overflow Score ($S_{\text{overflow}}$):** Weighted combination of underground sensor overflow probabilities:
   $$S_{\text{overflow}} = 0.65 \times p_{\text{15min}} + 0.35 \times p_{\text{30min}}$$
3. **Rainfall Score ($S_{\text{rainfall}}$):** Statistical percentile rank derived from the empirical historical rainfall distribution ($N=49,080$ records).
4. **Vulnerability Score ($S_{\text{vulnerability}}$):** Optional demographic/infrastructure vulnerability index (marked unavailable if not present).

#### Default Weight Distribution:
- $w_{\text{blockage}} = 0.35$
- $w_{\text{overflow}} = 0.45$
- $w_{\text{rainfall}} = 0.20$
- $w_{\text{vulnerability}} = 0.00$ *(optional)*

#### Risk Classification Thresholds:
| Risk Level | Score Range | Operational Response |
|---|---|---|
| **LOW** | $0.00 - 0.29$ | Routine scheduled monitoring |
| **MEDIUM** | $0.30 - 0.59$ | Heightened telemetry inspection |
| **HIGH** | $0.60 - 0.79$ | Pre-emptive maintenance dispatch |
---

## 🌐 REST API Backend

FloodSentinel includes a production-oriented **FastAPI** backend that exposes real-time inference endpoints for meteorological rainfall forecasting, sensor-based overflow prediction, and multi-modal risk ranking.

### Architecture

```text
FastAPI Server (api/main.py)
├── /api/health          → Service status & model readiness
├── /api/risk/predict    → Meteorological rainfall forecast (XGBoost + LSTM)
├── /api/risk/overflow   → Sensor telemetry overflow probability (XGBoost 15m/30m)
├── /api/alerts/rank     → Multi-modal site prioritization & risk scoring
└── /api/demo/risk       → Synthetic multi-catchment demonstration output
```

### Running the API

```bash
# Start FastAPI backend with hot-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive OpenAPI Documentation is available at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Environment Configuration

| Variable | Default | Description |
|---|---|---|
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8000` | API port |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173,...` | Allowed CORS origins for frontend client |
| `ENVIRONMENT` | `development` | Application runtime environment |

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health status and ML model readiness |
| `POST` | `/api/risk/predict` | Rainfall forecasting (12-month sequence → mm) |
| `POST` | `/api/risk/overflow` | Underground sensor overflow onset probabilities |
| `POST` | `/api/alerts/rank` | Multi-criteria drainage site ranking & risk scoring |
| `GET` | `/api/demo/risk` | Demonstration risk ranking over sample CCTV grates |

---

### Example Requests & Responses

#### 1. Rainfall Forecasting (`POST /api/risk/predict`)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/risk/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "subdivision": "ANDAMAN & NICOBAR ISLANDS",
       "target_month": 1,
       "rainfall_lags": [10.0, 20.0, 15.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0]
     }'
```

**Response (HTTP 200):**
```json
{
  "subdivision": "ANDAMAN & NICOBAR ISLANDS",
  "target_month": 1,
  "xgboost_prediction_mm": 77.87,
  "lstm_prediction_mm": 75.27,
  "average_prediction_mm": 76.57
}
```

#### 2. Overflow Prediction (`POST /api/risk/overflow`)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/risk/overflow" \
     -H "Content-Type: application/json" \
     -d '{
       "water_level_cm": 85.0,
       "rise_rate_cm_per_15min": 6.0,
       "rainfall_mm_per_hr": 25.0,
       "cumulative_rain_6hr_mm": 50.0,
       "cumulative_rain_24hr_mm": 100.0,
       "pipe_diameter_mm": 600.0,
       "pipe_material": "Concrete",
       "pipe_slope": 0.02,
       "elevation_m": 10.0,
       "month": 7
     }'
```

**Response (HTTP 200):**
```json
{
  "overflow_probability_15min": 0.2467,
  "overflow_probability_30min": 0.9291,
  "overflow_score": 0.4855
}
```

#### 3. Site Prioritization & Ranking (`POST /api/alerts/rank`)

**Request:**
```json
{
  "sites": [
    {
      "site_id": "CATCH_BASIN_042",
      "occlusion_percentage": 54.8,
      "overflow_probability_15min": 0.82,
      "overflow_probability_30min": 0.91,
      "rainfall_prediction_mm": 145.0,
      "vulnerability_score": null
    }
  ]
}
```

---

## ⚠️ Data Provenance & Production Limitations

- **Real Inference Models:** All ML inference (YOLO blockage detection, XGBoost overflow prediction, and XGBoost/LSTM rainfall forecasting) executes real, pre-trained model weights.
- **Decoupled Architecture:** The open-source CCTV imagery and sensor datasets originate from distinct public collections. The API does not hardcode false relationships; instead, it provides a clean data contract (`SiteAlertInput`) allowing municipal operators to bind live IoT sensor telemetry and CCTV RTSP streams per catchment site in production.

---

## License

Code is licensed under the MIT License.
Dataset is licensed under CC BY 4.0 (Roboflow).