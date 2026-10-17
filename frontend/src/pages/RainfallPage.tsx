import { useState } from 'react';
import { CloudRain, Send } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import { api } from '../services/api';
import type { RainfallPredictResponse } from '../types/api';
import { formatMonth } from '../utils/risk';

const SUBDIVISIONS = [
  'ANDAMAN & NICOBAR ISLANDS', 'ARUNACHAL PRADESH', 'ASSAM & MEGHALAYA',
  'BIHAR', 'CHHATTISGARH', 'COASTAL ANDHRA PRADESH', 'COASTAL KARNATAKA',
  'EAST MADHYA PRADESH', 'EAST RAJASTHAN', 'EAST UTTAR PRADESH',
  'GANGETIC WEST BENGAL', 'GUJARAT REGION', 'HARYANA DELHI & CHANDIGARH',
  'HIMACHAL PRADESH', 'JAMMU & KASHMIR', 'JHARKHAND',
  'KERALA', 'KONKAN & GOA', 'LAKSHADWEEP', 'MARATHWADA',
  'MATATHWADA', 'NAGA MANI MIZO TRIPURA', 'NORTH INTERIOR KARNATAKA',
  'NORTH MADHYA PRADESH', 'ORISSA', 'PUNJAB', 'RAYALASEEMA',
  'SAURASHTRA & KUTCH', 'SHWB & SIKKIM', 'SOUTH INTERIOR KARNATAKA',
  'SUB HIMALAYAN WEST BENGAL & SIKKIM', 'TAMIL NADU', 'TELANGANA',
  'UTTARAKHAND', 'VIDARBHA', 'WEST MADHYA PRADESH', 'WEST RAJASTHAN',
  'WEST UTTAR PRADESH',
];

const DEFAULT_LAGS = [5.0, 12.0, 18.0, 45.0, 110.0, 280.0, 320.0, 295.0, 210.0, 90.0, 30.0, 8.0];

export function RainfallPage() {
  const [subdivision, setSubdivision] = useState('KERALA');
  const [month, setMonth] = useState(7);
  const [lags, setLags] = useState<string>(DEFAULT_LAGS.join(', '));
  const [result, setResult] = useState<RainfallPredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const rainfall_lags = lags.split(',').map(v => parseFloat(v.trim()));
      if (rainfall_lags.length !== 12 || rainfall_lags.some(isNaN)) {
        throw new Error('Provide exactly 12 comma-separated numeric values for rainfall lags.');
      }
      const res = await api.predictRainfall({ subdivision, target_month: month, rainfall_lags });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  const lagValues = lags.split(',').map((v, i) => ({
    month: formatMonth(i + 1),
    mm: parseFloat(v.trim()) || 0,
  }));

  return (
    <div className="page-scroll fade-in">
      <div className="section-heading">
        <span className="hl" /><CloudRain size={18} /> Rainfall Forecast
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        {/* Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">XGBoost + LSTM Ensemble Prediction</div>
          </div>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="form-group">
              <label className="form-label">Meteorological Subdivision</label>
              <select className="form-select" value={subdivision} onChange={e => setSubdivision(e.target.value)}>
                {SUBDIVISIONS.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Target Month</label>
              <select className="form-select" value={month} onChange={e => setMonth(+e.target.value)}>
                {Array.from({ length: 12 }, (_, i) => (
                  <option key={i + 1} value={i + 1}>{formatMonth(i + 1)}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                Historical Rainfall Lags — 12 months [LAG_12 … LAG_1] (mm)
              </label>
              <textarea
                className="form-input"
                value={lags}
                onChange={e => setLags(e.target.value)}
                rows={3}
                style={{ resize: 'vertical', fontFamily: 'JetBrains Mono, monospace', fontSize: 12 }}
                placeholder="e.g. 5, 12, 18, 45, 110, 280, 320, 295, 210, 90, 30, 8"
              />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Ordered oldest → most-recent. Exactly 12 non-negative values required.
              </span>
            </div>

            {error && (
              <div style={{ fontSize: 12, color: 'var(--risk-critical)', padding: '8px 12px', background: 'rgba(239,68,68,0.1)', borderRadius: 6, border: '1px solid rgba(239,68,68,0.3)' }}>
                {error}
              </div>
            )}

            <button className="btn btn-primary" type="submit" disabled={loading}>
              <Send size={13} />
              {loading ? 'Predicting…' : 'Run Prediction'}
            </button>
          </form>
        </div>

        {/* Result */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {result && (
            <div className="card fade-in">
              <div className="card-header">
                <div className="card-title">Prediction Results</div>
                <span className="chip">{result.subdivision}</span>
              </div>
              <div className="grid-3" style={{ marginBottom: 16 }}>
                <ResultStat label="XGBoost" value={result.xgboost_prediction_mm.toFixed(1)} unit="mm" color="var(--accent-blue)" />
                <ResultStat label="LSTM" value={result.lstm_prediction_mm.toFixed(1)} unit="mm" color="var(--accent-cyan)" />
                <ResultStat label="Ensemble Avg" value={result.average_prediction_mm.toFixed(1)} unit="mm" color="var(--accent-teal)" bold />
              </div>
              <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Month: <strong style={{ color: 'var(--text-secondary)' }}>{formatMonth(result.target_month)}</strong> —
                Real XGBoost + LSTM models trained on IMD subdivision rainfall data.
              </p>
            </div>
          )}

          {/* Lag visualisation */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Input Lag Series (mm)</div>
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={lagValues} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)', fontSize: 12 }}
                  formatter={(v: number) => [`${v} mm`]}
                />
                <Line type="monotone" dataKey="mm" stroke="var(--accent-blue)" strokeWidth={2} dot={{ fill: 'var(--accent-blue)', r: 3 }} name="Rainfall (mm)" />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultStat({ label, value, unit, color, bold }: {
  label: string; value: string; unit: string; color: string; bold?: boolean;
}) {
  return (
    <div style={{ background: 'var(--bg-surface)', borderRadius: 8, padding: '12px 14px', border: `1px solid ${color}30` }}>
      <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase' as const, color: 'var(--text-muted)', marginBottom: 4, letterSpacing: '0.06em' }}>{label}</div>
      <div style={{ fontSize: bold ? 24 : 20, fontWeight: 800, color, fontVariantNumeric: 'tabular-nums' }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{unit}</div>
    </div>
  );
}
