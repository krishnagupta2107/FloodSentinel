import { ShieldCheck, Cpu, Database, Eye, Waves, CloudRain, GitBranch, AlertTriangle } from 'lucide-react';

export function AboutPage() {
  return (
    <div className="page-scroll fade-in">
      <div className="mb-4">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="hl" />
          FloodSentinel System Architecture & Data Provenance
        </h1>
        <p className="text-xs text-secondary mt-0.5">
          Municipal multi-modal urban flood intelligence, predictive hydrological ML pipelines, and integrity boundaries.
        </p>
      </div>

      {/* Provenance Alert Box */}
      <div className="p-4 rounded-lg bg-blue-950/30 border border-blue-500/30 text-xs text-secondary leading-relaxed mb-6">
        <div className="flex items-center gap-2 text-sm font-semibold text-blue-400 mb-2">
          <AlertTriangle size={16} />
          Operational Boundary & Scientific Data Provenance
        </div>
        <p className="mb-2">
          <strong>Real ML Models:</strong> The backend hosts fully trained, validated machine learning models:
          a fine-tuned YOLOv8 visual blockage detector, a trained XGBoost overflow onset classifier for sensor telemetry,
          and a dual XGBoost + LSTM monthly rainfall forecasting ensemble trained on IMD meteorological records.
        </p>
        <p>
          <strong>Demo Site Bindings:</strong> The demonstration endpoint (<code>/api/demo/risk</code>) binds these models
          to 10 synthetic scenario catchments (<code>SITE_CATCH_001</code> through <code>SITE_CATCH_010</code>). In this
          prototype build, no live municipal SCADA/CCTV feeds or live GIS shapefiles are connected. Coordinates and telemetry
          scenarios are simulated to illustrate the multi-modal fusion capabilities safely.
        </p>
      </div>

      {/* 4 Core Subsystem Cards */}
      <div className="grid-2 mb-6">
        {/* Model 1 */}
        <div className="card">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="p-2 rounded bg-blue-500/10 text-blue-400">
              <Eye size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Model 1: Drainage Blockage Detection</h2>
              <span className="text-[11px] text-muted">Ultralytics YOLOv8 Architecture</span>
            </div>
          </div>
          <p className="text-xs text-secondary leading-relaxed mb-3">
            Analyzes closed-circuit television (CCTV) or camera frames of stormwater grates, culverts, and street gutters.
            Detects garbage, vegetative silt, and debris to calculate an occlusion percentage and blockage severity score [0.0–1.0].
          </p>
          <div className="text-[11px] font-mono bg-surface p-2 rounded border border-muted text-cyan-300">
            Output: Occlusion % → Blockage Risk Severity Score
          </div>
        </div>

        {/* Model 2 */}
        <div className="card">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="p-2 rounded bg-cyan-500/10 text-cyan-400">
              <Waves size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Model 2: Overflow Onset Prediction</h2>
              <span className="text-[11px] text-muted">Gradient Boosted Decision Trees (XGBoost)</span>
            </div>
          </div>
          <p className="text-xs text-secondary leading-relaxed mb-3">
            Consumes physical drainage sensor telemetry: water level (cm), 15-minute rise velocity (cm/15min), rainfall intensity (mm/hr),
            pipe hydraulic diameter (mm), and elevation. Predicts probability of surface manhole overflow at 15-minute and 30-minute horizons.
          </p>
          <div className="text-[11px] font-mono bg-surface p-2 rounded border border-muted text-cyan-300">
            Output: P(Overflow 15m) &amp; P(Overflow 30m) → Surcharge Score
          </div>
        </div>

        {/* Model 3 */}
        <div className="card">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="p-2 rounded bg-teal-500/10 text-teal-400">
              <CloudRain size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Model 3: Rainfall Forecasting</h2>
              <span className="text-[11px] text-muted">Subdivision-Aware LSTM + XGBoost Ensemble</span>
            </div>
          </div>
          <p className="text-xs text-secondary leading-relaxed mb-3">
            Trained on historic meteorological subdivisions across India. Evaluates multi-month precipitation lag vectors
            to forecast upcoming monthly rainfall accumulation (mm) and normalized extreme deviation impact.
          </p>
          <div className="text-[11px] font-mono bg-surface p-2 rounded border border-muted text-cyan-300">
            Output: Predicted Rainfall (mm) → Normalized Precipitation Risk
          </div>
        </div>

        {/* Fusion Engine */}
        <div className="card">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="p-2 rounded bg-purple-500/10 text-purple-400">
              <Cpu size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Risk Fusion &amp; Prioritization Engine</h2>
              <span className="text-[11px] text-muted">Deterministic Multi-Modal Scoring Module</span>
            </div>
          </div>
          <p className="text-xs text-secondary leading-relaxed mb-3">
            Combines all modalities using domain-calibrated hydraulic weights: Blockage (0.35), Sensor Overflow (0.45),
            and Rainfall Forecast (0.20). Yields a single ranked composite score [0.0–1.0] and categorizes sites into LOW, MEDIUM, HIGH, or CRITICAL.
          </p>
          <div className="text-[11px] font-mono bg-surface p-2 rounded border border-muted text-cyan-300">
            Score = 0.35·B + 0.45·O + 0.20·R (+ optional vulnerability)
          </div>
        </div>
      </div>

      {/* Tech Stack Specs */}
      <div className="card">
        <h2 className="text-sm font-bold text-white mb-3">Technical Specifications</h2>
        <div className="grid-3 text-xs">
          <div className="p-3 rounded bg-surface border border-muted">
            <span className="text-muted block mb-1">Frontend Layer</span>
            <span className="font-semibold text-white block">React 18 + TypeScript + Vite</span>
            <span className="text-secondary block mt-0.5">Leaflet Maps, Recharts, Custom Glass UI</span>
          </div>
          <div className="p-3 rounded bg-surface border border-muted">
            <span className="text-muted block mb-1">Backend Inference Engine</span>
            <span className="font-semibold text-white block">FastAPI + Uvicorn</span>
            <span className="text-secondary block mt-0.5">Pydantic Schema Validation, JSON REST API</span>
          </div>
          <div className="p-3 rounded bg-surface border border-muted">
            <span className="text-muted block mb-1">Machine Learning Stack</span>
            <span className="font-semibold text-white block">PyTorch + XGBoost + Scikit-Learn</span>
            <span className="text-secondary block mt-0.5">YOLOv8, NumPy, Pandas, Joblib</span>
          </div>
        </div>
      </div>
    </div>
  );
}
