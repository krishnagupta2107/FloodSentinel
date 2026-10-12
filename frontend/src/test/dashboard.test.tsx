import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { OverviewPage } from '../pages/OverviewPage';
import { RiskTable } from '../components/ui/RiskTable';
import { FloodMap } from '../components/map/FloodMap';
import { DemoBanner } from '../components/ui/DemoBanner';
import { scorePercent, riskColor, riskBadgeClass } from '../utils/risk';
import type { SiteRankOutput } from '../types/api';

const mockSites: SiteRankOutput[] = [
  {
    rank: 1,
    site_id: 'SITE_CATCH_001',
    composite_risk_score: 0.88,
    risk_level: 'CRITICAL',
    blockage_score: 0.92,
    overflow_score: 0.85,
    rainfall_score: 0.75,
    vulnerability_score: 0.0,
    is_demo_data: true,
    components: { blockage: 0.92, overflow: 0.85, rainfall: 0.75 },
    metadata: { explanation: 'Severe obstruction requiring pump clearing.' },
  },
  {
    rank: 2,
    site_id: 'SITE_CATCH_002',
    composite_risk_score: 0.65,
    risk_level: 'HIGH',
    blockage_score: 0.45,
    overflow_score: 0.72,
    rainfall_score: 0.68,
    vulnerability_score: 0.0,
    is_demo_data: true,
    components: { blockage: 0.45, overflow: 0.72, rainfall: 0.68 },
    metadata: { explanation: 'High hydrodynamic surcharge in trunk line.' },
  },
  {
    rank: 3,
    site_id: 'SITE_CATCH_003',
    composite_risk_score: 0.32,
    risk_level: 'LOW',
    blockage_score: 0.15,
    overflow_score: 0.22,
    rainfall_score: 0.30,
    vulnerability_score: 0.0,
    is_demo_data: true,
    components: { blockage: 0.15, overflow: 0.22, rainfall: 0.30 },
    metadata: { explanation: 'Hydraulic conditions within standard limits.' },
  },
];

describe('Risk Utilities', () => {
  it('correctly maps risk colors and badges', () => {
    expect(riskColor('CRITICAL')).toBe('#ef4444');
    expect(riskColor('HIGH')).toBe('#f97316');
    expect(riskColor('MEDIUM')).toBe('#eab308');
    expect(riskColor('LOW')).toBe('#22c55e');

    expect(riskBadgeClass('CRITICAL')).toBe('badge-critical');
    expect(scorePercent(0.882)).toBe('88.2%');
  });
});

describe('Demo Banner', () => {
  it('clearly displays demo simulation notice and warnings', () => {
    render(<DemoBanner message="Synthetic catchment topology active." />);
    expect(screen.getByText(/DEMO MODE/i)).toBeInTheDocument();
    expect(screen.getByText(/Synthetic catchment topology active/i)).toBeInTheDocument();
  });
});

describe('Risk Table Component', () => {
  it('renders site ranking and handles search filtering', () => {
    render(<RiskTable sites={mockSites} />);

    // Renders all sites initially
    expect(screen.getByText('SITE_CATCH_001')).toBeInTheDocument();
    expect(screen.getByText('SITE_CATCH_002')).toBeInTheDocument();
    expect(screen.getByText('SITE_CATCH_003')).toBeInTheDocument();

    // Renders risk badges
    expect(screen.getAllByText('CRITICAL').length).toBeGreaterThan(0);

    // Search filter
    const searchInput = screen.getByPlaceholderText(/search by site id/i);
    fireEvent.change(searchInput, { target: { value: '002' } });

    expect(screen.queryByText('SITE_CATCH_001')).not.toBeInTheDocument();
    expect(screen.getByText('SITE_CATCH_002')).toBeInTheDocument();
  });

  it('filters rows by risk level chip', () => {
    render(<RiskTable sites={mockSites} />);

    const lowFilterBtn = screen.getByRole('button', { name: /^LOW$/i });
    fireEvent.click(lowFilterBtn);

    expect(screen.queryByText('SITE_CATCH_001')).not.toBeInTheDocument();
    expect(screen.getByText('SITE_CATCH_003')).toBeInTheDocument();
  });
});

describe('FloodMap Component', () => {
  it('renders without crashing even with arbitrary site IDs without pre-configured coordinates', () => {
    const arbitrarySites: SiteRankOutput[] = [
      {
        rank: 1,
        site_id: 'UNKNOWN_SITE_999',
        composite_risk_score: 0.75,
        risk_level: 'HIGH',
        blockage_score: 0.5,
        overflow_score: 0.6,
        rainfall_score: 0.7,
        vulnerability_score: 0.0,
        is_demo_data: true,
        components: {},
        metadata: {},
      },
    ];

    const { container } = render(<FloodMap sites={arbitrarySites} />);
    expect(container.querySelector('.flood-map-wrapper')).toBeInTheDocument();
    expect(screen.getByText(/DEMO MAP MODE/i)).toBeInTheDocument();
  });
});

describe('Overview Dashboard Page', () => {
  it('renders offline message when API status is offline', () => {
    render(
      <MemoryRouter>
        <OverviewPage status="offline" health={null} />
      </MemoryRouter>
    );

    expect(screen.getByText(/API Backend Offline/i)).toBeInTheDocument();
  });

  it('renders top KPI cards when connected', () => {
    render(
      <MemoryRouter>
        <OverviewPage
          status="online"
          health={{
            status: 'healthy',
            service: 'floodsentinel-api',
            version: '1.0.0',
            models: { rainfall: true, overflow: true, fusion: true },
          }}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Overall Risk')).toBeInTheDocument();
    expect(screen.getByText('Critical / High Alerts')).toBeInTheDocument();
    expect(screen.getByText('Monitored Sites')).toBeInTheDocument();
  });
});
