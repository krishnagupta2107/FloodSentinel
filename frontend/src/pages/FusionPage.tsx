import { useEffect } from 'react';
import { Activity, RefreshCw, AlertTriangle } from 'lucide-react';
import { useDemoRisk } from '../hooks/useDemoRisk';
import { DemoBanner } from '../components/ui/DemoBanner';
import { RiskTable } from '../components/ui/RiskTable';
import { RiskBarChart } from '../components/charts/RiskBarChart';
import { RiskRadar } from '../components/charts/RiskRadar';
import { riskColor } from '../utils/risk';

export function FusionPage() {
  const { data, loading, error, load } = useDemoRisk();

  useEffect(() => { load(); }, [load]);

  const topSite = data?.ranked_sites[0];

  return (
    <div className="page-scroll fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="section-heading">
          <span className="hl" /><Activity size={18} /> Risk Fusion — Multi-Modal Alert Ranking
        </div>
        <button className="btn btn-ghost" onClick={load} disabled={loading}>
          <RefreshCw size={13} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {data?.is_demo_data && <DemoBanner message={data.demo_warning} />}

      {error && (
        <div style={{ fontSize: 13, color: 'var(--risk-critical)', padding: '12px 16px', background: 'rgba(239,68,68,0.08)', borderRadius: 8, border: '1px solid rgba(239,68,68,0.25)', display: 'flex', gap: 8, alignItems: 'center' }}>
          <AlertTriangle size={14} />
          {error}
        </div>
      )}

      {loading && !data && (
        <div className="card empty-state"><div className="spinner" /><p>Loading fusion results…</p></div>
      )}

      {data && (
        <>
          {/* Summary stats */}
          <div className="grid-4">
            {(['CRITICAL','HIGH','MEDIUM','LOW'] as const).map(lvl => {
              const count = data.ranked_sites.filter(s => s.risk_level === lvl).length;
              return (
                <div key={lvl} className="stat-card" style={{ borderTop: `2px solid ${riskColor(lvl)}` }}>
                  <div className="stat-label">{lvl}</div>
                  <div className="stat-value" style={{ color: riskColor(lvl) }}>{count}</div>
                  <div className="stat-sub">sites</div>
                </div>
              );
            })}
          </div>

          {/* Bar chart + top-site radar */}
          <div className="grid-2">
            <div className="card">
              <div className="card-header">
                <div className="card-title">Composite Risk by Site</div>
              </div>
              <RiskBarChart sites={data.ranked_sites} />
            </div>

            {topSite && (
              <div className="card">
                <div className="card-header">
                  <div className="card-title">Highest Priority Site</div>
                  <span className="mono" style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{topSite.site_id}</span>
                </div>
                <RiskRadar site={topSite} />
                <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 8 }}>
                  <Metric label="Rank" value="#1" />
                  <Metric label="Score" value={`${((topSite.composite_risk_score ?? topSite.risk_score ?? 0) * 100).toFixed(1)}%`} color={riskColor(topSite.risk_level as any)} />
                  <Metric label="Level" value={topSite.risk_level} color={riskColor(topSite.risk_level as any)} />
                </div>
              </div>
            )}
          </div>

          {/* Full ranked table */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">All Sites — Ranked by Priority</div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{data.total_sites} sites</span>
            </div>
            <RiskTable sites={data.ranked_sites} />
          </div>

          {/* Fusion methodology */}
          <div className="card">
            <div className="card-header"><div className="card-title">Fusion Methodology</div></div>
            <div className="grid-3">
              <WeightCard label="YOLO Blockage" weight="35%" desc="Grate occlusion % from CCTV image analysis" color="var(--accent-blue)" />
              <WeightCard label="Sensor Overflow" weight="45%" desc="XGBoost dual-horizon overflow probability" color="var(--accent-cyan)" />
              <WeightCard label="Rainfall Forecast" weight="20%" desc="XGBoost + LSTM ensemble rainfall (mm)" color="var(--accent-teal)" />
            </div>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 12 }}>
              Vulnerability weight = 0% (no verified site metadata available).
              All demo site IDs and sensor values are synthetic — not real municipal locations.
            </p>
          </div>
        </>
      )}
    </div>
  );
}

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ textAlign: 'center' as const }}>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' as const, letterSpacing: '0.06em', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 16, fontWeight: 700, color: color ?? 'var(--text-primary)' }}>{value}</div>
    </div>
  );
}

function WeightCard({ label, weight, desc, color }: { label: string; weight: string; desc: string; color: string }) {
  return (
    <div style={{ background: 'var(--bg-surface)', borderRadius: 8, padding: '14px', border: `1px solid ${color}25` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>{label}</span>
        <span style={{ fontSize: 18, fontWeight: 800, color }}>{weight}</span>
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.5 }}>{desc}</p>
    </div>
  );
}
