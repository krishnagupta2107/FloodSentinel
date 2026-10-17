import { useState } from 'react';
import { Waves, Send } from 'lucide-react';
import { RadialBarChart, RadialBar, Legend, ResponsiveContainer, Tooltip } from 'recharts';
import { api } from '../services/api';
import type { OverflowPredictResponse } from '../types/api';
import { scorePercent } from '../utils/risk';

const PIPE_MATERIALS = ['Cast Iron', 'Concrete', 'PVC'];

const DEFAULTS = {
  water_level_cm: 85,
  rise_rate_cm_per_15min: 6,
  rainfall_mm_per_hr: 25,
  cumulative_rain_6hr_mm: 50,
  cumulative_rain_24hr_mm: 100,
  pipe_diameter_mm: 600,
  pipe_material: 'Concrete',
  pipe_slope: 0.02,
  elevation_m: 10,
  month: 7,
};

export function OverflowPage() {
  const [form, setForm] = useState(DEFAULTS);
  const [result, setResult] = useState<OverflowPredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set(k: keyof typeof DEFAULTS, v: string | number) {
    setForm(prev => ({ ...prev, [k]: v }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.predictOverflow({
        ...form,
        water_level_cm: +form.water_level_cm,
        rise_rate_cm_per_15min: +form.rise_rate_cm_per_15min,
        rainfall_mm_per_hr: +form.rainfall_mm_per_hr,
        cumulative_rain_6hr_mm: +form.cumulative_rain_6hr_mm,
        cumulative_rain_24hr_mm: +form.cumulative_rain_24hr_mm,
        pipe_diameter_mm: +form.pipe_diameter_mm,
        pipe_slope: +form.pipe_slope,
        elevation_m: +form.elevation_m,
        month: +form.month,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  const radialData = result
    ? [
        { name: '15-min', value: +(result.overflow_probability_15min * 100).toFixed(1), fill: '#3b82f6' },
        { name: '30-min', value: +(result.overflow_probability_30min * 100).toFixed(1), fill: '#06b6d4' },
        { name: 'Score', value:  +(result.overflow_score * 100).toFixed(1), fill: '#14b8a6' },
      ]
    : [];

  return (
    <div className="page-scroll fade-in">
      <div className="section-heading">
        <span className="hl" /><Waves size={18} /> Overflow Onset Prediction
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        {/* Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Sensor Telemetry Input</div>
          </div>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="grid-2">
              <F label="Water Level (cm)" type="number" value={form.water_level_cm} onChange={v => set('water_level_cm', v)} min={0} />
              <F label="Rise Rate (cm/15min)" type="number" value={form.rise_rate_cm_per_15min} onChange={v => set('rise_rate_cm_per_15min', v)} step={0.1} />
              <F label="Rainfall (mm/hr)" type="number" value={form.rainfall_mm_per_hr} onChange={v => set('rainfall_mm_per_hr', v)} min={0} />
              <F label="6hr Cumulative Rain (mm)" type="number" value={form.cumulative_rain_6hr_mm} onChange={v => set('cumulative_rain_6hr_mm', v)} min={0} />
              <F label="24hr Cumulative Rain (mm)" type="number" value={form.cumulative_rain_24hr_mm} onChange={v => set('cumulative_rain_24hr_mm', v)} min={0} />
              <F label="Pipe Diameter (mm)" type="number" value={form.pipe_diameter_mm} onChange={v => set('pipe_diameter_mm', v)} min={1} />
            </div>

            <div className="form-group">
              <label className="form-label">Pipe Material</label>
              <select className="form-select" value={form.pipe_material} onChange={e => set('pipe_material', e.target.value)}>
                {PIPE_MATERIALS.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>

            <div className="grid-2">
              <F label="Pipe Slope" type="number" value={form.pipe_slope} onChange={v => set('pipe_slope', v)} step={0.001} min={0} />
              <F label="Elevation (m)" type="number" value={form.elevation_m} onChange={v => set('elevation_m', v)} step={0.1} />
            </div>

            <div className="form-group">
              <label className="form-label">Month (1–12)</label>
              <input className="form-input" type="number" min={1} max={12} value={form.month} onChange={e => set('month', e.target.value)} />
            </div>

            {error && (
              <div style={{ fontSize: 12, color: 'var(--risk-critical)', padding: '8px 12px', background: 'rgba(239,68,68,0.1)', borderRadius: 6, border: '1px solid rgba(239,68,68,0.3)' }}>
                {error}
              </div>
            )}

            <button className="btn btn-primary" type="submit" disabled={loading}>
              <Send size={13} />
              {loading ? 'Predicting…' : 'Predict Overflow'}
            </button>
          </form>
        </div>

        {/* Result */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {result && (
            <div className="card fade-in">
              <div className="card-header">
                <div className="card-title">Overflow Risk Output</div>
              </div>
              <div className="grid-3" style={{ marginBottom: 16 }}>
                <ProbStat label="15-min" value={result.overflow_probability_15min} color="#3b82f6" />
                <ProbStat label="30-min" value={result.overflow_probability_30min} color="#06b6d4" />
                <ProbStat label="Risk Score" value={result.overflow_score} color="#14b8a6" />
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <RadialBarChart cx="50%" cy="50%" innerRadius={30} outerRadius={90} data={radialData} startAngle={90} endAngle={-270}>
                  <RadialBar dataKey="value" cornerRadius={4} label={{ position: 'insideStart', fill: '#94a3b8', fontSize: 11 }} />
                  <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)', fontSize: 12 }}
                    formatter={(v: number) => [`${v}%`]}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
                XGBoost model trained on synthetic sensor telemetry. Real sensor data from underground drainage network required for production use.
              </p>
            </div>
          )}

          {!result && !loading && (
            <div className="card empty-state">
              <Waves size={36} className="empty-icon" />
              <p>Submit sensor telemetry to see overflow probability predictions.</p>
            </div>
          )}

          {loading && (
            <div className="card empty-state">
              <div className="spinner" />
              <p>Running inference…</p>
            </div>
          )}

          {/* Info card */}
          <div className="card">
            <div className="card-header"><div className="card-title">Model Info</div></div>
            <ul style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.8, paddingLeft: 16 }}>
              <li>XGBoost trained on 10 hydraulic + meteorological features</li>
              <li>Dual-horizon: 15-min and 30-min overflow onset</li>
              <li>Composite score: 0.65 × P(15min) + 0.35 × P(30min)</li>
              <li>Pipe material encoded via ordinal encoding</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function F({ label, type, value, onChange, min, max, step }: {
  label: string; type: string; value: number | string;
  onChange: (v: string) => void; min?: number; max?: number; step?: number;
}) {
  return (
    <div className="form-group">
      <label className="form-label">{label}</label>
      <input className="form-input" type={type} value={value} min={min} max={max} step={step ?? 1}
        onChange={e => onChange(e.target.value)} />
    </div>
  );
}

function ProbStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ background: 'var(--bg-surface)', borderRadius: 8, padding: '12px 14px', border: `1px solid ${color}30`, textAlign: 'center' as const }}>
      <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase' as const, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color, fontVariantNumeric: 'tabular-nums' }}>{scorePercent(value)}</div>
    </div>
  );
}
