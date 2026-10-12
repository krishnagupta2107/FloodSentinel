import { useEffect, useState } from 'react';
import {
  Activity, CloudRain, Waves, AlertTriangle, CheckCircle,
  XCircle, Eye, ShieldAlert, RefreshCw, MapPin, ListFilter
} from 'lucide-react';
import type { ApiStatus, HealthResponse, DemoRiskResponse, SiteRankOutput } from '../types/api';
import { api } from '../services/api';
import { DemoBanner } from '../components/ui/DemoBanner';
import { RiskBarChart } from '../components/charts/RiskBarChart';
import { RiskTable } from '../components/ui/RiskTable';
import { FloodMap } from '../components/map/FloodMap';
import { SiteDetailModal } from '../components/dashboard/SiteDetailModal';
import { riskColor, scorePercent } from '../utils/risk';

interface OverviewProps {
  status: ApiStatus;
  health: HealthResponse | null;
  onRetry?: () => void;
}

export function OverviewPage({ status, health, onRetry }: OverviewProps) {
  const [demo, setDemo] = useState<DemoRiskResponse | null>(null);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [selectedSite, setSelectedSite] = useState<SiteRankOutput | null>(null);
  const [viewTab, setViewTab] = useState<'map' | 'chart'>('map');

  const loadData = () => {
    if (status === 'online') {
      setLoadingDemo(true);
      api.demoRisk()
        .then(setDemo)
        .catch(() => setDemo(null))
        .finally(() => setLoadingDemo(false));
    }
  };

  useEffect(() => {
    loadData();
  }, [status]);

  const sites = demo?.ranked_sites ?? [];
  const critical = sites.filter((s) => s.risk_level === 'CRITICAL').length;
  const high = sites.filter((s) => s.risk_level === 'HIGH').length;
  const criticalOrHigh = critical + high;

  // Aggregate metrics
  const maxScore = sites.length > 0 ? Math.max(...sites.map((s) => s.composite_risk_score)) : 0;
  const topSite = sites.length > 0 ? sites[0] : null;

  // Rainfall forecast average or top site forecast
  const avgRainfallScore = sites.length > 0
    ? sites.reduce((acc, s) => acc + (s.rainfall_score ?? 0), 0) / sites.length
    : 0;

  // Overflow risk average
  const avgOverflowScore = sites.length > 0
    ? sites.reduce((acc, s) => acc + (s.overflow_score ?? 0), 0) / sites.length
    : 0;

  // Blockage alerts (>50% blockage score)
  const blockageAlerts = sites.filter((s) => (s.blockage_score ?? 0) >= 0.5).length;

  return (
    <div className="page-scroll fade-in">
      {/* Top Banner if Demo data */}
      {demo?.is_demo_data && <DemoBanner message={demo.demo_warning} />}

      {/* Header with quick refresh */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="hl" />
            Command Overview & Flood Risk Intelligence
          </h1>
          <p className="text-xs text-secondary mt-0.5">
            Real-time multi-modal fusion combining YOLOv8 blockage, IoT overflow telemetry, and rainfall forecasting.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {status === 'offline' && onRetry && (
            <button type="button" className="btn btn-primary" onClick={onRetry}>
              <RefreshCw size={13} /> Reconnect API
            </button>
          )}
          <button
            type="button"
            className="btn btn-ghost"
            onClick={loadData}
            disabled={loadingDemo || status !== 'online'}
            title="Refresh simulation data"
          >
            <RefreshCw size={13} className={loadingDemo ? 'spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* 6 Top-level KPI cards requested in Section 6 */}
      <div className="grid-6">
        <KpiCard
          label="Overall Risk"
          value={sites.length > 0 ? scorePercent(maxScore) : '—'}
          sub={topSite ? `Peak: ${topSite.site_id}` : 'No active alerts'}
          accent={maxScore >= 0.8 ? 'accent-red' : maxScore >= 0.6 ? 'accent-orange' : 'accent-blue'}
          icon={<AlertTriangle size={16} color={maxScore >= 0.8 ? '#ef4444' : '#3b82f6'} />}
        />
        <KpiCard
          label="Critical / High Alerts"
          value={loadingDemo ? '…' : String(criticalOrHigh)}
          sub={`${critical} critical, ${high} high`}
          accent="accent-red"
          icon={<ShieldAlert size={16} color="#ef4444" />}
        />
        <KpiCard
          label="Monitored Sites"
          value={loadingDemo ? '…' : String(sites.length)}
          sub={demo?.is_demo_data ? 'Simulation Catchments' : 'Active telemetry sites'}
          accent="accent-cyan"
          icon={<Activity size={16} color="var(--accent-cyan)" />}
        />
        <KpiCard
          label="Forecast Rainfall"
          value={loadingDemo ? '…' : `${(avgRainfallScore * 100).toFixed(0)}%`}
          sub="Mean regional impact"
          accent="accent-teal"
          icon={<CloudRain size={16} color="var(--accent-teal)" />}
        />
        <KpiCard
          label="Overflow Risk"
          value={loadingDemo ? '…' : `${(avgOverflowScore * 100).toFixed(0)}%`}
          sub="Mean onset probability"
          accent="accent-orange"
          icon={<Waves size={16} color="#f97316" />}
        />
        <KpiCard
          label="Blockage Alerts"
          value={loadingDemo ? '…' : String(blockageAlerts)}
          sub="Drainage occlusions ≥50%"
          accent="accent-blue"
          icon={<Eye size={16} color="#3b82f6" />}
        />
      </div>

      {/* Backend Offline Warning Card */}
      {status === 'offline' && (
        <div className="card text-center p-8 border-red-500/30 bg-red-950/20">
          <XCircle size={38} color="#ef4444" className="mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">API Backend Offline</h3>
          <p className="text-xs text-secondary max-w-lg mx-auto mb-4">
            Cannot connect to the FloodSentinel FastAPI server at <code className="mono text-cyan-400">http://localhost:8000</code>.
            Launch the backend to evaluate live or demo risk scenarios:
          </p>
          <pre className="inline-block bg-base px-3 py-1.5 rounded text-xs mono text-cyan-300 border border-muted mb-4">
            uvicorn api.main:app --reload
          </pre>
          <div>
            <button type="button" className="btn btn-primary inline-flex" onClick={onRetry}>
              <RefreshCw size={13} /> Retry API Connection
            </button>
          </div>
        </div>
      )}

      {/* Model Readiness Row */}
      {health && (
        <div className="card">
          <div className="card-header">
            <div className="card-title text-sm">System Subsystem Readiness</div>
            <span className="text-xs text-muted font-mono">v{health.version}</span>
          </div>
          <div className="flex gap-4 flex-wrap">
            <ModelStatus label="Model 1: YOLOv8 Drainage Blockage" ready={health.models.fusion} icon={<Eye size={14} />} />
            <ModelStatus label="Model 2: XGBoost Sensor Overflow" ready={health.models.overflow} icon={<Waves size={14} />} />
            <ModelStatus label="Model 3: XGBoost + LSTM Rainfall" ready={health.models.rainfall} icon={<CloudRain size={14} />} />
            <ModelStatus label="Risk Fusion Prioritization Engine" ready={health.models.fusion} icon={<Activity size={14} />} />
          </div>
        </div>
      )}

      {/* Central Interactive Map & Visual Analytics Section */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center gap-2">
            <MapPin size={16} className="text-blue-400" />
            <span className="card-title">Geospatial Catchment Map & Priority Visualization</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className={`filter-chip ${viewTab === 'map' ? 'active' : ''}`}
              onClick={() => setViewTab('map')}
            >
              Interactive Map
            </button>
            <button
              type="button"
              className={`filter-chip ${viewTab === 'chart' ? 'active' : ''}`}
              onClick={() => setViewTab('chart')}
            >
              Risk Bar Distribution
            </button>
          </div>
        </div>

        {viewTab === 'map' ? (
          <FloodMap
            sites={sites}
            selectedSiteId={selectedSite?.site_id}
            onSelectSite={(site) => setSelectedSite(site)}
            height={440}
          />
        ) : (
          <div className="p-4">
            <RiskBarChart sites={sites} />
          </div>
        )}
      </div>

      {/* Ranked Priority Table (Section 8) */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center gap-2">
            <ListFilter size={16} className="text-cyan-400" />
            <span className="card-title">Multi-Modal Risk Prioritization Queue</span>
          </div>
          <span className="text-xs text-muted">
            {sites.length} sites ranked by composite severity
          </span>
        </div>

        <RiskTable
          sites={sites}
          selectedSiteId={selectedSite?.site_id}
          onSelectSite={(site) => setSelectedSite(site)}
        />
      </div>

      {/* Detail Inspection Modal (Section 9) */}
      {selectedSite && (
        <SiteDetailModal
          site={selectedSite}
          onClose={() => setSelectedSite(null)}
        />
      )}
    </div>
  );
}

function KpiCard({
  label,
  value,
  sub,
  accent,
  icon,
}: {
  label: string;
  value: string;
  sub: string;
  accent: string;
  icon: React.ReactNode;
}) {
  return (
    <div className={`stat-card ${accent}`}>
      <div className="flex justify-between items-start mb-2">
        <span className="stat-label">{label}</span>
        {icon}
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-sub">{sub}</div>
    </div>
  );
}

function ModelStatus({
  label,
  ready,
  icon,
}: {
  label: string;
  ready: boolean;
  icon: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-2.5 px-3.5 py-2 rounded bg-surface border border-muted flex-1 min-w-[200px]">
      <span style={{ color: ready ? '#22c55e' : '#64748b' }}>{icon}</span>
      <span className="text-xs font-medium text-secondary flex-1">{label}</span>
      <span
        className="text-[10px] font-bold px-1.5 py-0.5 rounded tracking-wide uppercase"
        style={{
          background: ready ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
          color: ready ? '#22c55e' : '#ef4444',
        }}
      >
        {ready ? 'Ready' : 'Not Loaded'}
      </span>
    </div>
  );
}
