import React, { useState, useMemo } from 'react';
import { ArrowUpDown, Search, Eye, Filter } from 'lucide-react';
import { riskBadgeClass, riskColor, scorePercent } from '../../utils/risk';
import { ScoreGauge } from '../ui/ScoreGauge';
import type { SiteRankOutput, RiskLevel } from '../../types/api';

interface RiskTableProps {
  sites: SiteRankOutput[];
  selectedSiteId?: string | null;
  onSelectSite?: (site: SiteRankOutput) => void;
}

type SortField = 'rank' | 'site_id' | 'composite_risk_score' | 'blockage_score' | 'overflow_score' | 'rainfall_score';
type SortOrder = 'asc' | 'desc';

export function RiskTable({ sites, selectedSiteId, onSelectSite }: RiskTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRisk, setSelectedRisk] = useState<RiskLevel | 'ALL'>('ALL');
  const [sortField, setSortField] = useState<SortField>('rank');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  const filteredAndSortedSites = useMemo(() => {
    let result = [...sites];

    // Search filter
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      result = result.filter(
        (s) =>
          s.site_id.toLowerCase().includes(q) ||
          s.risk_level.toLowerCase().includes(q)
      );
    }

    // Risk level filter
    if (selectedRisk !== 'ALL') {
      result = result.filter((s) => s.risk_level === selectedRisk);
    }

    // Sorting
    result.sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      // Handle nulls / undefined
      if (valA === undefined) valA = 0 as any;
      if (valB === undefined) valB = 0 as any;

      if (typeof valA === 'string' && typeof valB === 'string') {
        return sortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortOrder === 'asc' ? (valA as number) - (valB as number) : (valB as number) - (valA as number);
    });

    return result;
  }, [sites, searchTerm, selectedRisk, sortField, sortOrder]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder(field === 'rank' ? 'asc' : 'desc');
    }
  };

  if (!sites.length) {
    return (
      <div className="empty-state">
        <p>No site data available.</p>
      </div>
    );
  }

  return (
    <div className="risk-table-container">
      {/* Search and Filter Controls */}
      <div className="table-toolbar">
        <div className="table-search-input-wrapper">
          <Search size={14} className="search-icon" />
          <input
            type="text"
            className="table-search-input"
            placeholder="Search by site ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="table-filters">
          <Filter size={13} className="text-muted" />
          {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((lvl) => {
            const active = selectedRisk === lvl;
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
                onClick={() => setSelectedRisk(lvl)}
              >
                {lvl}
              </button>
            );
          })}
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('rank')} className="cursor-pointer">
                <span className="th-content">
                  # <ArrowUpDown size={11} />
                </span>
              </th>
              <th onClick={() => handleSort('site_id')} className="cursor-pointer">
                <span className="th-content">
                  Site ID <ArrowUpDown size={11} />
                </span>
              </th>
              <th>Risk Level</th>
              <th onClick={() => handleSort('composite_risk_score')} className="cursor-pointer">
                <span className="th-content">
                  Score <ArrowUpDown size={11} />
                </span>
              </th>
              <th onClick={() => handleSort('blockage_score')} className="cursor-pointer">
                <span className="th-content">
                  Blockage <ArrowUpDown size={11} />
                </span>
              </th>
              <th onClick={() => handleSort('overflow_score')} className="cursor-pointer">
                <span className="th-content">
                  Overflow <ArrowUpDown size={11} />
                </span>
              </th>
              <th onClick={() => handleSort('rainfall_score')} className="cursor-pointer">
                <span className="th-content">
                  Rainfall <ArrowUpDown size={11} />
                </span>
              </th>
              <th>Dominant Factor</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedSites.map((site) => {
              const isSelected = selectedSiteId === site.site_id;
              const isRankOne = site.rank === 1;

              const blockage = site.blockage_score ?? site.components?.blockage ?? 0;
              const overflow = site.overflow_score ?? site.components?.overflow ?? 0;
              const rainfall = site.rainfall_score ?? site.components?.rainfall ?? 0;

              let dominant = 'Blockage';
              if (overflow > blockage && overflow > rainfall) dominant = 'Overflow';
              else if (rainfall > blockage && rainfall > overflow) dominant = 'Rainfall';

              return (
                <tr
                  key={site.site_id}
                  className={`${isSelected ? 'selected-row' : ''} ${isRankOne ? 'rank-one-row' : ''}`}
                  onClick={() => onSelectSite && onSelectSite(site)}
                >
                  <td className="rank-cell">
                    {isRankOne ? (
                      <span className="rank-badge-top">1</span>
                    ) : (
                      site.rank
                    )}
                  </td>
                  <td>
                    <span className="mono font-semibold">{site.site_id}</span>
                    {site.is_demo_data && (
                      <span className="chip" style={{ marginLeft: 6, fontSize: 9 }}>DEMO</span>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${riskBadgeClass(site.risk_level as RiskLevel)}`}>
                      {site.risk_level}
                    </span>
                  </td>
                  <td style={{ fontWeight: 700, color: riskColor(site.risk_level as RiskLevel) }}>
                    {scorePercent(site.composite_risk_score)}
                  </td>
                  <td>
                    <MiniBar value={blockage} color="var(--accent-blue)" />
                  </td>
                  <td>
                    <MiniBar value={overflow} color="var(--accent-cyan)" />
                  </td>
                  <td>
                    <MiniBar value={rainfall} color="var(--accent-teal)" />
                  </td>
                  <td>
                    <span className="text-xs text-secondary font-medium">{dominant}</span>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-ghost table-inspect-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onSelectSite) onSelectSite(site);
                      }}
                      title="Inspect site details"
                    >
                      <Eye size={13} />
                      Inspect
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MiniBar({ value, color }: { value: number; color: string }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, minWidth: 80 }}>
      <div className="progress-bar" style={{ flex: 1 }}>
        <div
          className="progress-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span style={{ fontSize: 11, color: 'var(--text-secondary)', minWidth: 32, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
        {pct}%
      </span>
    </div>
  );
}
