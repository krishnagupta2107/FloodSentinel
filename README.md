# FloodSentinel 🌊

![CI](https://github.com/krishnagupta2107/FloodSentinel/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Model](https://img.shields.io/badge/model-YOLOv8m-orange)

**AI-powered storm drain blockage detection and flash-flood early warning.**  
Detects blockages in CCTV drain footage, estimates occlusion severity, and feeds a risk engine to prioritise maintenance before floods start.

> B.Tech CSE (AIML) Mini-Project — GLA University, Mathura | Team 166  
> Mentor: Dr. Anuja Bhargava

---

## What It Does

| Stage | What happens |
|-------|-------------|
| 📷 **Detect** | YOLOv8m identifies drainage blockages from CCTV images |
| 📐 **Estimate** | Occlusion % of the drain grate is calculated from detected bounding boxes |
| 📈 **Predict** | LSTM / XGBoost estimates overflow risk from rainfall + water-level time-series |
| 🗺️ **Alert** | Risk-ranked sites are displayed on an interactive map dashboard |

---

## Architecture

```
CCTV Image ──► YOLOv8m ──► Occlusion Estimator ──┐
                                                   ▼
Rainfall + Water Level ──► LSTM / XGBoost ──► Risk Scorer ──► Map Dashboard
```

**Detected Classes:** `Defects` · `Sewage blockage`

---

## Results

### YOLOv8m Optimized Model (50 epochs, 999 images)

| Metric | Score |
|--------|-------|
| mAP@0.5 | 0.686 |
| mAP@0.5:0.95 | 0.403 |

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

## Quickstart

```bash
git clone https://github.com/krishnagupta2107/FloodSentinel.git
cd FloodSentinel
python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt
```

### Run inference on an image
```bash
python src/floodsentinel/estimate_occlusion.py "path/to/drain.jpg"
```

### Train YOLO Model
```bash
python src/floodsentinel/train.py --size m --epochs 50
```

### Predict Rainfall (LSTM + XGBoost)
```python
from src.floodsentinel.models.rainfall_predictor import RainfallPredictor

predictor = RainfallPredictor()
result = predictor.predict(
    previous_12_months=[120, 90, 55, 30, 15, 200, 350, 300, 250, 180, 100, 60],
    subdivision="EAST UTTAR PRADESH",
    target_month=7
)
print(result)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Computer Vision | PyTorch · YOLOv8 · OpenCV |
| Prediction | LSTM (PyTorch) · XGBoost |
| Backend | FastAPI |
| Frontend | React.js · Leaflet.js |
| Database | PostgreSQL / PostGIS |

---

## Roadmap

- [x] YOLOv8 baseline (Nano) — mAP 0.689
- [x] Occlusion % estimation
- [x] YOLOv8m optimized model
- [x] LSTM / XGBoost overflow-risk model
- [ ] FastAPI backend
- [ ] React + Leaflet dashboard
- [ ] End-to-end pipeline demo

---

## Project Structure

```
FloodSentinel/
├── src/floodsentinel/
│   ├── estimate_occlusion.py        # Occlusion % from YOLO detections
│   ├── train.py                     # YOLOv8 training script (GPU, augmentations)
│   ├── batch_inference.py           # Run model on full test set
│   ├── plot_results.py              # Visualise detections
│   └── models/
│       └── rainfall_predictor.py    # LSTM + XGBoost rainfall forecasting
├── models/                          # Saved model weights & scalers
│   ├── rainfall_lstm.keras
│   ├── rainfall_xgboost.json
│   └── *.pkl                        # Scalers & encoders
├── rainfall_lstm_xgboost/           # Rainfall training data (gitignored)
├── Yolo Dataset/                    # Train/valid/test images + labels
├── configs/                         # Training config YAML
├── tests/                           # Unit tests (pytest)
└── .github/workflows/ci.yml         # Lint CI (ruff + black)
```

---

## References

1. Jocher, G. et al. (2023). *YOLO by Ultralytics*. https://github.com/ultralytics/ultralytics
2. *Storm Drain Model Dataset* — Roboflow, CC BY 4.0. https://universe.roboflow.com/cv-revvg/storm-drain-model-cjhye
3. *Rainfall in India* — Kaggle. https://www.kaggle.com/datasets/rajanand/rainfall-in-india

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

## 🖥️ Interactive Frontend Dashboard

FloodSentinel includes a command-center React dashboard providing municipal operators with real-time multi-modal risk intelligence, geospatial visualization, and priority dispatch queues.

### 🏗️ Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/       # RiskBarChart, RiskRadar
│   │   ├── dashboard/    # SiteDetailModal
│   │   ├── layout/       # Sidebar (responsive), TopBar (model health pills)
│   │   ├── map/          # FloodMap (interactive Leaflet with risk markers)
│   │   └── ui/           # ScoreGauge, RiskTable, DemoBanner
│   ├── hooks/            # useApiHealth, useDemoRisk
│   ├── pages/            # OverviewPage, SitesPage, AlertsPage, FusionPage,
│   │                     # RainfallPage, OverflowPage, DemoPage, AboutPage
│   ├── services/         # Centralized API service with TypeScript interfaces
│   ├── types/            # API schemas and UI contracts
│   ├── utils/            # Risk color palettes, badges, formatting
│   ├── App.tsx           # Route layout with command center header
│   └── main.tsx          # React application root
├── package.json
└── vite.config.ts        # Vite build & test configuration with backend proxy
```

### ⚙️ Setup & Execution

#### Terminal 1 — Start the FastAPI Backend:
```bash
# Activate virtual environment
source .venv/bin/activate

# Launch API server
uvicorn api.main:app --reload --port 8000
```

#### Terminal 2 — Start the React Dashboard:
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Dashboard will be available at `http://localhost:5173`.

### 🧪 Frontend Testing & Build

```bash
cd frontend

# Run unit tests (10 tests covering API service, risk formatting, map safety, and UI filters)
npm test

# Build production bundle
npm run build
```

### 🔧 Configuration & Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | `""` (proxied to `http://localhost:8000` via Vite) | Backend API endpoint URL |

### ⚠️ Geospatial Map & Demo Mode Notes

- **Synthetic Bindings:** The `GET /api/demo/risk` endpoint feeds 10 synthetic scenario catchments (`SITE_CATCH_001` through `SITE_CATCH_010`) to safely illustrate multi-modal fusion.
- **Simulated Map Coordinates:** Coordinates rendered in the interactive Leaflet map are simulated visualization coordinates for testing. Real municipal GIS shapefiles or live municipal GPS coordinates are not hardcoded in the codebase.
- **Live Readiness:** Production deployments bind live sensor telemetry and CCTV frames to the `/api/alerts/rank` endpoint using genuine catchment identifiers.

---

## License

Code: [MIT](LICENSE) · Dataset: CC BY 4.0 (Roboflow)