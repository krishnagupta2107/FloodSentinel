import { useState, useEffect } from 'react';
import { Layers, RefreshCw, AlertTriangle, Search, Filter, Eye } from 'lucide-react';
import { useDemoRisk } from '../hooks/useDemoRisk';
import { DemoBanner } from '../components/ui/DemoBanner';
import { FloodMap } from '../components/map/FloodMap';
import { SiteDetailModal } from '../components/dashboard/SiteDetailModal';
import { RiskTable } from '../components/ui/RiskTable';
import type { SiteRankOutput } from '../types/api';
import { riskColor, riskBadgeClass, scorePercent } from '../utils/risk';

export function SitesPage() {
  const { data, loading, error, load } = useDemoRisk();
  const [selectedSite, setSelectedSite] = useState<SiteRankOutput | null>(null);
  const [activeTab, setActiveTab] = useState<'grid' | 'table' | 'map'>('table');

  useEffect(() => {
    load();
  }, [load]);

  const sites = data?.ranked_sites ?? [];

  return (
    <div className="page-scroll fade-in">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="hl" />
            <Layers size={20} className="text-cyan-400" />
            Catchment Site Directory & Inventory
          </h1>
          <p className="text-xs text-secondary mt-0.5">
            Full registry of urban drainage monitoring locations, telemetry sensors, and visual assessment nodes.
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

      {/* Tab Switcher */}
      <div className="flex gap-2 mb-4 border-b border-muted pb-3">
        <button
          type="button"
          className={`filter-chip ${activeTab === 'table' ? 'active' : ''}`}
          onClick={() => setActiveTab('table')}
        >
          Ranked Table View
        </button>
        <button
          type="button"
          className={`filter-chip ${activeTab === 'grid' ? 'active' : ''}`}
          onClick={() => setActiveTab('grid')}
        >
          Site Cards Grid
        </button>
        <button
          type="button"
          className={`filter-chip ${activeTab === 'map' ? 'active' : ''}`}
          onClick={() => setActiveTab('map')}
        >
          Map Inspection
        </button>
      </div>

      {/* View Contents */}
      {activeTab === 'table' && (
        <div className="card">
          <RiskTable
            sites={sites}
            selectedSiteId={selectedSite?.site_id}
            onSelectSite={(site) => setSelectedSite(site)}
          />
        </div>
      )}

      {activeTab === 'grid' && (
        <div className="grid-3">
          {sites.map((site) => {
            const color = riskColor(site.risk_level as any);
            return (
              <div
                key={site.site_id}
                className="card hover:border-blue-500/50 transition cursor-pointer"
                onClick={() => setSelectedSite(site)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="mono font-bold text-white text-sm">{site.site_id}</span>
                    <div className="text-[10px] text-muted font-mono mt-0.5">Priority Rank #{site.rank}</div>
                  </div>
                  <span className={`badge ${riskBadgeClass(site.risk_level as any)}`}>
                    {site.risk_level}
                  </span>
                </div>

                <div className="flex items-baseline justify-between my-3">
                  <span className="text-xs text-secondary">Composite Risk:</span>
                  <span className="text-lg font-bold" style={{ color }}>
                    {scorePercent(site.composite_risk_score)}
                  </span>
                </div>

                <div className="space-y-1.5 text-xs text-secondary border-t border-muted pt-2.5">
                  <div className="flex justify-between">
                    <span>Blockage Score:</span>
                    <span className="text-white font-mono">{((site.blockage_score ?? 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Overflow Score:</span>
                    <span className="text-white font-mono">{((site.overflow_score ?? 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Rainfall Score:</span>
                    <span className="text-white font-mono">{((site.rainfall_score ?? 0) * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <button
                  type="button"
                  className="btn btn-ghost w-full mt-3 text-xs justify-center"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedSite(site);
                  }}
                >
                  <Eye size={12} /> Inspect Telemetry
                </button>
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'map' && (
        <div className="card">
          <FloodMap
            sites={sites}
            selectedSiteId={selectedSite?.site_id}
            onSelectSite={(site) => setSelectedSite(site)}
            height={550}
          />
        </div>
      )}

      {selectedSite && (
        <SiteDetailModal
          site={selectedSite}
          onClose={() => setSelectedSite(null)}
        />
      )}
    </div>
  );
}
