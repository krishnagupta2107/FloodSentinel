import { riskColor } from '../../utils/risk';
import type { RiskLevel } from '../../types/api';

interface ScoreGaugeProps {
  score: number | null | undefined; // 0–1
  level: RiskLevel | string;
  size?: number;
}

export function ScoreGauge({ score, level, size = 72 }: ScoreGaugeProps) {
  const safeScore = typeof score === 'number' && Number.isFinite(score)
    ? Math.max(0, Math.min(1, score))
    : 0;

  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const fill = circ * (1 - safeScore);
  const color = riskColor(level as RiskLevel);

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
      {/* Background track */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="#e2e8f0"
        strokeWidth={6}
      />
      {/* Active risk arc */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={6}
        strokeDasharray={circ}
        strokeDashoffset={fill}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
      />
    </svg>
  );
}
