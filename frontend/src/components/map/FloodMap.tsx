import { useState, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { Info, MapPin, ZoomIn, ZoomOut, RotateCcw, AlertTriangle, ShieldCheck } from 'lucide-react';
import type { SiteRankOutput, RiskLevel } from '../../types/api';
import { riskColor, riskBadgeClass, scorePercent } from '../../utils/risk';

// Simulated base coordinates for demo demonstration (e.g., urban catchment grid)
const DEMO_BASE_LAT = 10.026;
const DEMO_BASE_LNG = 76.312;

// Offset table for 10 demo sites so they distribute across an urban grid
const SITE_COORDINATES: Record<string, [number, number]> = {
  SITE_CATCH_001: [10.028, 76.315],
  SITE_CATCH_002: [10.035, 76.322],
  SITE_CATCH_003: [10.021, 76.308],
  SITE_CATCH_004: [10.015, 76.325],
  SITE_CATCH_005: [10.040, 76.305],
  SITE_CATCH_006: [10.018, 76.335],
  SITE_CATCH_007: [10.032, 76.298],
  SITE_CATCH_008: [10.010, 76.318],
  SITE_CATCH_009: [10.025, 76.330],
  SITE_CATCH_010: [10.038, 76.318],
};

function getSiteCoordinates(siteId: string, index: number): [number, number] {
  if (SITE_COORDINATES[siteId]) {
    return SITE_COORDINATES[siteId];
  }
  // Algorithmic deterministic spread for any arbitrary site ID
  const angle = (index * 36) * (Math.PI / 180);
  const radius = 0.012 + (index % 3) * 0.008;
  return [
    DEMO_BASE_LAT + radius * Math.cos(angle),
    DEMO_BASE_LNG + radius * Math.sin(angle),
  ];
}

interface FloodMapProps {
  sites: SiteRankOutput[];
  selectedSiteId?: string | null;
  onSelectSite?: (site: SiteRankOutput) => void;
  height?: number | string;
}

function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  return (
    <div className="map-custom-controls">
      <button
        type="button"
        className="map-ctrl-btn"
        title="Zoom In"
        onClick={() => map.zoomIn()}
      >
        <ZoomIn size={14} />
      </button>
      <button
        type="button"
        className="map-ctrl-btn"
        title="Zoom Out"
        onClick={() => map.zoomOut()}
      >
        <ZoomOut size={14} />
      </button>
      <button
        type="button"
        className="map-ctrl-btn"
        title="Reset Map Center"
        onClick={() => map.setView(center, zoom)}
      >
        <RotateCcw size={14} />
      </button>
    </div>
  );
}

export function FloodMap({
  sites,
  selectedSiteId,
  onSelectSite,
  height = 460,
}: FloodMapProps) {
  const [levelFilter, setLevelFilter] = useState<RiskLevel | 'ALL'>('ALL');
  const [tileTheme, setTileTheme] = useState<'dark' | 'osm'>('dark');

  const filteredSites = useMemo(() => {
    if (levelFilter === 'ALL') return sites;
    return sites.filter((s) => s.risk_level === levelFilter);
  }, [sites, levelFilter]);

  const centerPos: [number, number] = [DEMO_BASE_LAT, DEMO_BASE_LNG];

  return (
    <div className="flood-map-wrapper">
      {/* Simulation / Data Provenance Banner */}
      <div className="map-disclaimer-banner">
        <AlertTriangle size={13} className="text-amber-400" />
        <span>
          <strong>DEMO MAP MODE:</strong> Geospatial coordinates are simulated
          visualization positions. Not bound to live municipal GIS or operational CCTV.
        </span>
      </div>

      {/* Top Filter Bar */}
      <div className="map-filter-toolbar">
        <div className="filter-group">
          <span className="filter-label">Filter Risk:</span>
          {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((lvl) => {
            const active = levelFilter === lvl;
            const color = lvl === 'ALL' ? 'var(--text-secondary)' : riskColor(lvl as RiskLevel);
            return (
              <button
                key={lvl}
                type="button"
                className={`filter-chip ${active ? 'active' : ''}`}
                style={
                  active && lvl !== 'ALL'
                    ? { borderColor: color, color, backgroundColor: `${color}20` }
                    : {}
                }
                onClick={() => setLevelFilter(lvl)}
              >
                {lvl}
              </button>
            );
          })}
        </div>

        <div className="filter-group">
          <span className="filter-label">Tiles:</span>
          <button
            type="button"
            className={`filter-chip ${tileTheme === 'dark' ? 'active' : ''}`}
            onClick={() => setTileTheme('dark')}
          >
            Dark Carto
          </button>
          <button
            type="button"
            className={`filter-chip ${tileTheme === 'osm' ? 'active' : ''}`}
            onClick={() => setTileTheme('osm')}
          >
            OpenStreetMap
          </button>
        </div>
      </div>

      {/* Leaflet Container */}
      <div style={{ height, width: '100%', position: 'relative' }}>
        <MapContainer
          center={centerPos}
          zoom={13}
          style={{ height: '100%', width: '100%', background: '#060b14' }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url={
              tileTheme === 'dark'
                ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
                : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            }
          />

          <MapController center={centerPos} zoom={13} />

          {filteredSites.map((site, index) => {
            const pos = getSiteCoordinates(site.site_id, index);
            const color = riskColor(site.risk_level as RiskLevel);
            const isSelected = selectedSiteId === site.site_id;
            const radius = site.risk_level === 'CRITICAL' ? 14 : site.risk_level === 'HIGH' ? 12 : 9;

            // Extract dominant factor from components
            const blockageScore = site.blockage_score ?? site.components?.blockage ?? 0;
            const overflowScore = site.overflow_score ?? site.components?.overflow ?? 0;
            const rainfallScore = site.rainfall_score ?? site.components?.rainfall ?? 0;

            let dominantFactor = 'Blockage';
            if (overflowScore > blockageScore && overflowScore > rainfallScore) dominantFactor = 'Overflow Telemetry';
            else if (rainfallScore > blockageScore && rainfallScore > overflowScore) dominantFactor = 'Rainfall Intensity';

            const explanation = (site.metadata?.explanation as string) ||
              `Composite flood risk is ${site.risk_level} (${scorePercent(site.composite_risk_score)}) driven primarily by ${dominantFactor}.`;

            return (
              <CircleMarker
                key={site.site_id}
                center={pos}
                radius={radius}
                pathOptions={{
                  color: isSelected ? '#ffffff' : color,
                  weight: isSelected ? 3 : 2,
                  fillColor: color,
                  fillOpacity: isSelected ? 0.9 : 0.65,
                }}
                eventHandlers={{
                  click: () => {
                    if (onSelectSite) onSelectSite(site);
                  },
                }}
              >
                <Popup className="flood-map-popup">
                  <div className="popup-content">
                    <div className="popup-header">
                      <span className="mono font-bold text-sm text-white">{site.site_id}</span>
                      <span className={`badge ${riskBadgeClass(site.risk_level as RiskLevel)}`}>
                        {site.risk_level}
                      </span>
                    </div>

                    <div className="popup-score-row">
                      <span className="text-xs text-muted">Composite Risk:</span>
                      <span className="text-base font-bold" style={{ color }}>
                        {scorePercent(site.composite_risk_score)}
                      </span>
                      <span className="text-xs text-muted">Rank #{site.rank}</span>
                    </div>

                    <div className="popup-metrics-grid">
                      <div className="metric-box">
                        <span className="metric-lbl">Blockage</span>
                        <span className="metric-val">{(blockageScore * 100).toFixed(0)}%</span>
                      </div>
                      <div className="metric-box">
                        <span className="metric-lbl">Overflow</span>
                        <span className="metric-val">{(overflowScore * 100).toFixed(0)}%</span>
                      </div>
                      <div className="metric-box">
                        <span className="metric-lbl">Rainfall</span>
                        <span className="metric-val">{(rainfallScore * 100).toFixed(0)}%</span>
                      </div>
                    </div>

                    <div className="popup-explanation">
                      <strong>Dominant:</strong> {dominantFactor}
                      <p className="mt-1 text-xs opacity-90">{explanation}</p>
                    </div>

                    {onSelectSite && (
                      <button
                        type="button"
                        className="btn btn-primary popup-action-btn"
                        onClick={() => onSelectSite(site)}
                      >
                        Inspect Site Details
                      </button>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>

      {/* Legend below map */}
      <div className="map-legend-bar">
        <div className="legend-title">Risk Hierarchy:</div>
        {(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((lvl) => (
          <div key={lvl} className="legend-item">
            <span
              className="legend-dot"
              style={{ backgroundColor: riskColor(lvl) }}
            />
            <span className="legend-label">{lvl}</span>
          </div>
        ))}
        <div className="legend-info">
          <Info size={12} />
          <span>Click any marker to view sensor breakdown and municipal explanation.</span>
        </div>
      </div>
    </div>
  );
}
