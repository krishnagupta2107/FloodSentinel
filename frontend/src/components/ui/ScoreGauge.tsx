import { riskColor } from '../../utils/risk';
import type { RiskLevel } from '../../types/api';

interface ScoreGaugeProps {
  score: number;        // 0–1
  level: RiskLevel;
  size?: number;
}

export function ScoreGauge({ score, level, size = 72 }: ScoreGaugeProps) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const fill = circ * (1 - score);
  const color = riskColor(level);

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none"
        stroke="rgba(255,255,255,0.06)"
        strokeWidth={6}
      />
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none"
        stroke={color}
        strokeWidth={6}
        strokeDasharray={circ}
        strokeDashoffset={fill}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.6s cubic-bezier(0.4,0,0.2,1)', filter: `drop-shadow(0 0 4px ${color})` }}
      />
    </svg>
  );
}
