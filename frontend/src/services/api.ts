import type {
  HealthResponse,
  RainfallPredictRequest,
  RainfallPredictResponse,
  OverflowTelemetryInput,
  OverflowPredictResponse,
  RankAlertsResponse,
  DemoRiskResponse,
  SiteAlertInput,
} from '../types/api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  /** GET /api/health */
  health(): Promise<HealthResponse> {
    return request<HealthResponse>('/api/health');
  },

  /** POST /api/risk/predict — Rainfall forecasting */
  predictRainfall(payload: RainfallPredictRequest): Promise<RainfallPredictResponse> {
    return request<RainfallPredictResponse>('/api/risk/predict', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /** POST /api/risk/overflow — Overflow onset prediction */
  predictOverflow(payload: OverflowTelemetryInput): Promise<OverflowPredictResponse> {
    return request<OverflowPredictResponse>('/api/risk/overflow', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /** POST /api/alerts/rank — Multi-modal risk fusion ranking */
  rankAlerts(sites: SiteAlertInput[]): Promise<RankAlertsResponse> {
    return request<RankAlertsResponse>('/api/alerts/rank', {
      method: 'POST',
      body: JSON.stringify({ sites }),
    });
  },

  /** GET /api/demo/risk — Synthetic demo risk evaluation */
  demoRisk(): Promise<DemoRiskResponse> {
    return request<DemoRiskResponse>('/api/demo/risk');
  },
};
