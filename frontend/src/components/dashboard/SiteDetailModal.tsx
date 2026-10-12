import React from 'react';
import { X, AlertTriangle, CloudRain, Waves, Eye, ShieldAlert, Cpu } from 'lucide-react';
import type { SiteRankOutput, RiskLevel } from '../../types/api';
import { riskColor, riskBadgeClass, scorePercent } from '../../utils/risk';
import { ScoreGauge } from '../ui/ScoreGauge';

interface SiteDetailModalProps {
  site: SiteRankOutput | null;
  onClose: () => void;
}

export function SiteDetailModal({ site, onClose }: SiteDetailModalProps) {
  if (!site) return null;

  const color = riskColor(site.risk_level as RiskLevel);
  const blockageScore = site.blockage_score ?? site.components?.blockage ?? 0;
  const overflowScore = site.overflow_score ?? site.components?.overflow ?? 0;
  const rainfallScore = site.rainfall_score ?? site.components?.rainfall ?? 0;
  const vulnScore = site.vulnerability_score ?? site.components?.vulnerability ?? 0;

  // Metadata items
  const metadata = site.metadata || {};
  const explanation = (metadata.explanation as string) ||
    `Risk priority rank #${site.rank} with composite severity ${scorePercent(site.composite_risk_score)}. Multi-modal weighting applies blockage severity and short-horizon overflow risk.`;

  const rainfallMm = (metadata.rainfall_prediction_mm as number) ?? (metadata.rainfall_mm as number);
  const overflow15 = (metadata.overflow_prob_15min as number) ?? (metadata.overflow_15m as number);
  const overflow30 = (metadata.overflow_prob_30min as number) ?? (metadata.overflow_30m as number);
  const occlusion = (metadata.occlusion_pct as number) ?? (metadata.blockage_pct as number);
  const imageName = (metadata.image_name as string) ?? (metadata.yolo_image as string);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="flex items-center gap-3">
            <span className="mono font-bold text-lg text-white">{site.site_id}</span>
            <span className={`badge ${riskBadgeClass(site.risk_level as RiskLevel)}`}>
              {site.risk_level}
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
              Priority Rank #{site.rank}
            </span>
            {site.is_demo_data && (
              <span className="chip" style={{ fontSize: 9 }}>DEMO DATA</span>
            )}
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Top Summary Banner */}
          <div className="site-summary-grid">
            <div className="summary-gauge-card">
              <ScoreGauge score={site.composite_risk_score} level={site.risk_level as RiskLevel} size={110} />
              <div className="mt-2 text-center">
                <span className="text-xs text-secondary uppercase tracking-wider">Composite Score</span>
                <div className="text-xl font-bold" style={{ color }}>
                  {scorePercent(site.composite_risk_score)}
                </div>
              </div>
            </div>

            <div className="summary-breakdown-card">
              <div className="card-subtitle text-xs uppercase tracking-wider text-muted mb-2">
                Multi-Modal Weight Breakdown
              </div>
              <div className="space-y-3">
                <BarContribution
                  label="Drainage Blockage (YOLOv8)"
                  score={blockageScore}
                  color="var(--accent-blue)"
                  icon={<Eye size={14} />}
                />
                <BarContribution
                  label="Sensor Overflow Telemetry"
                  score={overflowScore}
                  color="var(--accent-cyan)"
                  icon={<Waves size={14} />}
                />
                <BarContribution
                  label="Subdivision Rainfall Forecast"
                  score={rainfallScore}
                  color="var(--accent-teal)"
                  icon={<CloudRain size={14} />}
                />
                {vulnScore > 0 && (
                  <BarContribution
                    label="Catchment Vulnerability"
                    score={vulnScore}
                    color="var(--risk-medium)"
                    icon={<ShieldAlert size={14} />}
                  />
                )}
              </div>
            </div>
          </div>

          {/* Forecast & Telemetry Indicators */}
          <div className="section-title text-sm font-semibold text-white mt-4 mb-2 flex items-center gap-2">
            <Cpu size={14} className="text-cyan-400" />
            Forward-Looking Projections
          </div>

          <div className="grid-3">
            <div className="kpi-mini-card">
              <span className="kpi-lbl">Rainfall Forecast</span>
              <span className="kpi-val text-teal-400">
                {rainfallMm !== undefined ? `${rainfallMm.toFixed(1)} mm` : `${(rainfallScore * 100).toFixed(0)} score`}
              </span>
              <span className="kpi-sub">LSTM / XGBoost ensemble</span>
            </div>
            <div className="kpi-mini-card">
              <span className="kpi-lbl">Overflow Onset (15 min)</span>
              <span className="kpi-val text-blue-400">
                {overflow15 !== undefined ? `${(overflow15 * 100).toFixed(1)}%` : `${(overflowScore * 100).toFixed(0)}%`}
              </span>
              <span className="kpi-sub">Sensor-based gradient model</span>
            </div>
            <div className="kpi-mini-card">
              <span className="kpi-lbl">Overflow Onset (30 min)</span>
              <span className="kpi-val text-amber-400">
                {overflow30 !== undefined ? `${(overflow30 * 100).toFixed(1)}%` : 'Projected window'}
              </span>
              <span className="kpi-sub">30-minute lookahead horizon</span>
            </div>
          </div>

          {/* Model Explanation */}
          <div className="explanation-box mt-4">
            <div className="flex items-center gap-2 mb-1 text-xs font-semibold text-accent">
              <AlertTriangle size={13} />
              Fusion Engine Diagnostic Rationale
            </div>
            <p className="text-xs text-secondary leading-relaxed">
              {explanation}
            </p>
          </div>

          {/* CCTV Image reference if available */}
          {imageName && (
            <div className="mt-3 text-xs text-muted flex items-center justify-between p-2 rounded bg-surface border border-muted">
              <span>Linked YOLO Vision Frame:</span>
              <span className="mono text-white">{imageName}</span>
              {occlusion !== undefined && (
                <span className="text-amber-400">Occlusion: {occlusion.toFixed(1)}%</span>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <div className="text-xs text-muted">
            {site.is_demo_data ? '⚠️ Simulation Binding (Demo Mode)' : 'Municipal Site Record'}
          </div>
          <button type="button" className="btn btn-primary" onClick={onClose}>
            Close Inspection
          </button>
        </div>
      </div>
    </div>
  );
}

function BarContribution({
  label,
  score,
  color,
  icon,
}: {
  label: string;
  score: number;
  color: string;
  icon: React.ReactNode;
}) {
  const pct = Math.max(0, Math.min(100, Math.round(score * 100)));
  return (
    <div>
      <div className="flex justify-between text-xs mb-1 text-secondary">
        <span className="flex items-center gap-1.5">
          <span style={{ color }}>{icon}</span>
          {label}
        </span>
        <span className="font-mono font-medium text-white">{pct}%</span>
      </div>
      <div className="progress-bar h-2">
        <div
          className="progress-fill h-2"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
