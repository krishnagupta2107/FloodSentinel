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

---

## License

Code: [MIT](LICENSE) · Dataset: CC BY 4.0 (Roboflow)