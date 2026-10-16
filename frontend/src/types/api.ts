// API response types mirroring the FastAPI Pydantic schemas

export interface ModelReadiness {
  rainfall: boolean;
  overflow: boolean;
  fusion: boolean;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  models: ModelReadiness;
}

export interface RainfallPredictRequest {
  subdivision: string;
  target_month: number;
  rainfall_lags: number[];
}

export interface RainfallPredictResponse {
  subdivision: string;
  target_month: number;
  xgboost_prediction_mm: number;
  lstm_prediction_mm: number;
  average_prediction_mm: number;
}

export interface OverflowTelemetryInput {
  water_level_cm: number;
  rise_rate_cm_per_15min: number;
  rainfall_mm_per_hr: number;
  cumulative_rain_6hr_mm: number;
  cumulative_rain_24hr_mm: number;
  pipe_diameter_mm: number;
  pipe_material: string;
  pipe_slope: number;
  elevation_m: number;
  month: number;
}

export interface OverflowPredictResponse {
  overflow_probability_15min: number;
  overflow_probability_30min: number;
  overflow_score: number;
}

export interface SiteAlertInput {
  site_id: string;
  image_name?: string;
  occlusion_percentage?: number;
  overflow?: OverflowTelemetryInput;
  overflow_probability_15min?: number;
  overflow_probability_30min?: number;
  rainfall_prediction_mm?: number;
  vulnerability_score?: number;
  metadata?: Record<string, unknown>;
}

export interface FactorBreakdownItem {
  raw_score: number;
  weight: number;
  weighted_contribution: number;
  percentage_share: number;
}

export interface SiteRankOutput {
  rank: number;
  site_id: string;
  risk_score: number;
  composite_risk_score?: number;
  risk_level: string;
  image_name?: string | null;
  occlusion_percentage?: number | null;
  blockage_score: number;
  overflow_probability_15min?: number | null;
  overflow_probability_30min?: number | null;
  overflow_score: number;
  rainfall_prediction_mm?: number | null;
  rainfall_score: number;
  vulnerability_score?: number | null;
  vulnerability_available?: boolean;
  dominant_risk_factor: string;
  explanation: string;
  factor_breakdown?: Record<string, FactorBreakdownItem>;
  is_demo_data?: boolean;
  components?: Record<string, number>;
  metadata?: Record<string, unknown>;
}

export interface RankAlertsResponse {
  ranked_sites: SiteRankOutput[];
  total_sites: number;
  is_demo_data?: boolean;
}

export interface DemoRiskResponse {
  ranked_sites: SiteRankOutput[];
  total_sites: number;
  is_demo_data: boolean;
  notice: string;
  demo_warning?: string;
}

// UI-specific types
export type ApiStatus = 'connecting' | 'online' | 'offline';
export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';

export interface SiteMarker {
  id: string;
  lat: number;
  lng: number;
  risk_level: RiskLevel;
  score: number;
  is_demo: boolean;
}
