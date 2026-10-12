import type { RiskLevel } from '../types/api';

export function riskColor(level: RiskLevel): string {
  switch (level) {
    case 'CRITICAL': return '#ef4444';
    case 'HIGH':     return '#f97316';
    case 'MEDIUM':   return '#eab308';
    case 'LOW':      return '#22c55e';
    default:         return '#64748b';
  }
}

export function riskBg(level: RiskLevel): string {
  switch (level) {
    case 'CRITICAL': return 'rgba(239,68,68,0.15)';
    case 'HIGH':     return 'rgba(249,115,22,0.15)';
    case 'MEDIUM':   return 'rgba(234,179,8,0.15)';
    case 'LOW':      return 'rgba(34,197,94,0.15)';
    default:         return 'rgba(100,116,139,0.10)';
  }
}

export function riskBadgeClass(level: RiskLevel): string {
  switch (level) {
    case 'CRITICAL': return 'badge-critical';
    case 'HIGH':     return 'badge-high';
    case 'MEDIUM':   return 'badge-medium';
    case 'LOW':      return 'badge-low';
    default:         return 'badge-none';
  }
}

export function scorePercent(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

export function formatMonth(m: number): string {
  return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m - 1] ?? `M${m}`;
}

export function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}
