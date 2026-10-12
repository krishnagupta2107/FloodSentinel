import { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, Clock, Truck, Wrench, RefreshCw, Eye } from 'lucide-react';
import { useDemoRisk } from '../hooks/useDemoRisk';
import { DemoBanner } from '../components/ui/DemoBanner';
import { SiteDetailModal } from '../components/dashboard/SiteDetailModal';
import type { SiteRankOutput, RiskLevel } from '../types/api';
import { riskColor, riskBadgeClass, scorePercent } from '../utils/risk';

export function AlertsPage() {
  const { data, loading, error, load } = useDemoRisk();
  const [selectedSite, setSelectedSite] = useState<SiteRankOutput | null>(null);
  const [acknowledged, setAcknowledged] = useState<Record<string, boolean>>({});

  useEffect(() => {
    load();
  }, [load]);

  const sites = data?.ranked_sites ?? [];
  const urgentSites = sites.filter(
    (s) => s.risk_level === 'CRITICAL' || s.risk_level === 'HIGH'
  );

  const toggleAck = (siteId: string) => {
    setAcknowledged((prev) => ({ ...prev, [siteId]: !prev[siteId] }));
  };

  return (
    <div className="page-scroll fade-in">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="hl" />
            <ShieldAlert size={20} className="text-red-400" />
            Emergency Incident & Alert Dispatch Queue
          </h1>
          <p className="text-xs text-secondary mt-0.5">
            Prioritized high-consequence flood risk triggers requiring municipal crew intervention or pump dispatch.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={load}
          disabled={loading}
        >
          <RefreshCw size={13} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {data?.is_demo_data && <DemoBanner message={data.demo_warning} />}

      {error && (
        <div className="p-3 rounded bg-red-900/20 border border-red-500/30 text-xs text-red-400 flex items-center gap-2 mb-4">
          <AlertTriangle size={14} />
          <span>{error}</span>
        </div>
      )}

      {/* Summary KPI banner */}
      <div className="grid-3 mb-4">
        <div className="stat-card accent-red">
          <div className="stat-label">Active Urgent Alerts</div>
          <div className="stat-value text-red-400">{urgentSites.length}</div>
          <div className="stat-sub">CRITICAL and HIGH threshold violations</div>
        </div>
        <div className="stat-card accent-orange">
          <div className="stat-label">Action Status</div>
          <div className="stat-value text-amber-400">
            {Object.values(acknowledged).filter(Boolean).length} / {urgentSites.length}
          </div>
          <div className="stat-sub">Acknowledged / dispatched by operator</div>
        </div>
        <div className="stat-card accent-blue">
          <div className="stat-label">Recommended Response Protocol</div>
          <div className="stat-value text-blue-400">&lt; 15 min</div>
          <div className="stat-sub">Fast onset mitigation window</div>
        </div>
      </div>

      {/* Incident List */}
      <div className="space-y-3">
        {urgentSites.map((site) => {
          const isAck = acknowledged[site.site_id];
          const color = riskColor(site.risk_level as RiskLevel);
          const blockage = site.blockage_score ?? site.components?.blockage ?? 0;
          const overflow = site.overflow_score ?? site.components?.overflow ?? 0;
          const rainfall = site.rainfall_score ?? site.components?.rainfall ?? 0;

          let dominant = 'Blockage Obstruction';
          let actionRecommendation = 'Dispatch vacuum / debris clearing vehicle to unblock culvert intake.';
          let actionIcon = <Wrench size={14} />;

          if (overflow > blockage && overflow > rainfall) {
            dominant = 'Hydrodynamic Surcharge / Overflow';
            actionRecommendation = 'Deploy mobile diesel dewatering pump unit to relieve manhole pressure.';
            actionIcon = <Truck size={14} />;
          } else if (rainfall > blockage && rainfall > overflow) {
            dominant = 'High-Intensity Precipitation Influx';
            actionRecommendation = 'Alert downstream low-lying residential sectors; activate retention spillway.';
            actionIcon = <Clock size={14} />;
          }

          return (
            <div
              key={site.site_id}
              className={`card transition border-l-4 ${isAck ? 'opacity-70' : ''}`}
              style={{ borderLeftColor: color }}
            >
              <div className="flex justify-between items-start flex-wrap gap-2">
                <div className="flex items-center gap-3">
                  <span className="mono font-bold text-white text-base">{site.site_id}</span>
                  <span className={`badge ${riskBadgeClass(site.risk_level as RiskLevel)}`}>
                    {site.risk_level}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-surface border border-muted font-mono text-secondary">
                    Priority Rank #{site.rank}
                  </span>
                  <span className="text-xs font-semibold" style={{ color }}>
                    Severity: {scorePercent(site.composite_risk_score)}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="btn btn-ghost text-xs"
                    onClick={() => setSelectedSite(site)}
                  >
                    <Eye size={12} /> Inspect Detail
                  </button>
                  <button
                    type="button"
                    className={`btn text-xs ${isAck ? 'btn-ghost text-green-400' : 'btn-primary'}`}
                    onClick={() => toggleAck(site.site_id)}
                  >
                    {isAck ? (
                      <>
                        <CheckCircle2 size={13} /> Dispatched / Ack
                      </>
                    ) : (
                      'Acknowledge & Dispatch'
                    )}
                  </button>
                </div>
              </div>

              {/* Action recommendation box */}
              <div className="mt-3 p-3 rounded bg-surface border border-muted flex items-start gap-3">
                <div className="p-1.5 rounded bg-blue-500/10 text-blue-400 mt-0.5">
                  {actionIcon}
                </div>
                <div className="flex-1">
                  <div className="text-xs font-semibold text-white">
                    Dominant Driver: <span className="text-cyan-400">{dominant}</span>
                  </div>
                  <p className="text-xs text-secondary mt-0.5">
                    <strong>Recommended Action:</strong> {actionRecommendation}
                  </p>
                </div>
              </div>

              {/* Mini metrics bar */}
              <div className="flex gap-4 mt-3 text-xs text-muted font-mono pt-2 border-t border-muted">
                <span>Blockage: {(blockage * 100).toFixed(0)}%</span>
                <span>Overflow: {(overflow * 100).toFixed(0)}%</span>
                <span>Rainfall: {(rainfall * 100).toFixed(0)}%</span>
              </div>
            </div>
          );
        })}

        {urgentSites.length === 0 && !loading && (
          <div className="card text-center p-8">
            <CheckCircle2 size={36} color="#22c55e" className="mx-auto mb-2" />
            <h3 className="text-base font-bold text-white mb-1">No Urgent Alerts</h3>
            <p className="text-xs text-secondary">
              All monitored drainage catchments are within normal baseline tolerances.
            </p>
          </div>
        )}
      </div>

      {selectedSite && (
        <SiteDetailModal
          site={selectedSite}
          onClose={() => setSelectedSite(null)}
        />
      )}
    </div>
  );
}
