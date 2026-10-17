import type { RiskLevel, SiteRankOutput } from '../types/api';

export const OVERALL_RISK_TOOLTIP =
  'Overall risk combines the available blockage, overflow and rainfall indicators. Missing inputs are excluded from the calculation.';

export function getRiskScore(site: Partial<SiteRankOutput> | null | undefined): number {
  if (!site) return 0;
  const raw = site.risk_score ?? site.composite_risk_score;
  if (raw === null || raw === undefined || typeof raw !== 'number' || !Number.isFinite(raw)) {
    return 0;
  }
  return Math.max(0, Math.min(1, raw));
}

export function riskColor(level: RiskLevel | string): string {
  switch (level) {
    case 'CRITICAL':
      return '#dc2626'; // Red 600
    case 'HIGH':
      return '#ea580c'; // Orange 600
    case 'MEDIUM':
      return '#d97706'; // Amber 600
    case 'LOW':
      return '#16a34a'; // Green 600
    default:
      return '#64748b'; // Slate 500
  }
}

export function riskBg(level: RiskLevel | string): string {
  switch (level) {
    case 'CRITICAL':
      return '#fef2f2'; // Red 50
    case 'HIGH':
      return '#fff7ed'; // Orange 50
    case 'MEDIUM':
      return '#fffbeb'; // Amber 50
    case 'LOW':
      return '#f0fdf4'; // Green 50
    default:
      return '#f8fafc'; // Slate 50
  }
}

export function riskBorder(level: RiskLevel | string): string {
  switch (level) {
    case 'CRITICAL':
      return '#fecaca'; // Red 200
    case 'HIGH':
      return '#fed7aa'; // Orange 200
    case 'MEDIUM':
      return '#fde68a'; // Amber 200
    case 'LOW':
      return '#bbf7d0'; // Green 200
    default:
      return '#e2e8f0'; // Slate 200
  }
}

export function riskBadgeClass(level: RiskLevel | string): string {
  switch (level) {
    case 'CRITICAL':
      return 'badge-critical';
    case 'HIGH':
      return 'badge-high';
    case 'MEDIUM':
      return 'badge-medium';
    case 'LOW':
      return 'badge-low';
    default:
      return 'badge-none';
  }
}

export function scorePercent(score: number | null | undefined): string {
  if (score === null || score === undefined || typeof score !== 'number' || !Number.isFinite(score)) {
    return 'Unavailable';
  }
  const clamped = Math.max(0, Math.min(1, score));
  return `${(clamped * 100).toFixed(1)}%`;
}

export function formatMetric(
  val: number | null | undefined,
  unit: string = '',
  digits: number = 1
): string {
  if (val === null || val === undefined || typeof val !== 'number' || !Number.isFinite(val)) {
    return 'Unavailable';
  }
  return unit ? `${val.toFixed(digits)} ${unit}` : val.toFixed(digits);
}

export function formatMonth(m: number): string {
  return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m - 1] ?? `M${m}`;
}

export function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}
