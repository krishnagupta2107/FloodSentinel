import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../services/api';
import type { HealthResponse, DemoRiskResponse } from '../types/api';

describe('FloodSentinel API Service', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches health status correctly', async () => {
    const mockHealth: HealthResponse = {
      status: 'healthy',
      service: 'floodsentinel-api',
      version: '1.0.0',
      models: {
        rainfall: true,
        overflow: true,
        fusion: true,
      },
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealth,
    } as Response);

    const res = await api.health();
    expect(res.status).toBe('healthy');
    expect(res.models.rainfall).toBe(true);
    expect(res.models.overflow).toBe(true);
  });

  it('fetches demo risk dataset with simulation notice', async () => {
    const mockDemo: DemoRiskResponse = {
      total_sites: 2,
      is_demo_data: true,
      demo_warning: 'Simulation demo data only',
      ranked_sites: [
        {
          rank: 1,
          site_id: 'SITE_CATCH_001',
          composite_risk_score: 0.88,
          risk_level: 'CRITICAL',
          blockage_score: 0.9,
          overflow_score: 0.85,
          rainfall_score: 0.8,
          vulnerability_score: 0.0,
          is_demo_data: true,
          components: { blockage: 0.9, overflow: 0.85, rainfall: 0.8 },
          metadata: { explanation: 'Severe culvert blockage combined with rising water' },
        },
        {
          rank: 2,
          site_id: 'SITE_CATCH_002',
          composite_risk_score: 0.45,
          risk_level: 'MEDIUM',
          blockage_score: 0.3,
          overflow_score: 0.4,
          rainfall_score: 0.5,
          vulnerability_score: 0.0,
          is_demo_data: true,
          components: { blockage: 0.3, overflow: 0.4, rainfall: 0.5 },
          metadata: { explanation: 'Moderate water rise under normal flow' },
        },
      ],
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockDemo,
    } as Response);

    const res = await api.demoRisk();
    expect(res.is_demo_data).toBe(true);
    expect(res.total_sites).toBe(2);
    expect(res.ranked_sites[0].site_id).toBe('SITE_CATCH_001');
    expect(res.ranked_sites[0].risk_level).toBe('CRITICAL');
  });

  it('throws descriptive error on API failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'Internal Server Error',
    } as Response);

    await expect(api.health()).rejects.toThrow('API 500: Internal Server Error');
  });
});
