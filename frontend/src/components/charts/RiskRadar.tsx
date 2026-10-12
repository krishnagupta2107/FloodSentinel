import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip,
} from 'recharts';
import type { SiteRankOutput } from '../../types/api';
import { riskColor } from '../../utils/risk';

interface RadarProps {
  site: SiteRankOutput;
}

export function RiskRadar({ site }: RadarProps) {
  const data = [
    { axis: 'Blockage', value: +(site.blockage_score * 100).toFixed(1) },
    { axis: 'Overflow', value: +(site.overflow_score * 100).toFixed(1) },
    { axis: 'Rainfall', value: +(site.rainfall_score * 100).toFixed(1) },
    { axis: 'Composite', value: +(site.composite_risk_score * 100).toFixed(1) },
  ];
  const color = riskColor(site.risk_level as any);

  return (
    <ResponsiveContainer width="100%" height={180}>
      <RadarChart data={data}>
        <PolarGrid stroke="rgba(255,255,255,0.08)" />
        <PolarAngleAxis dataKey="axis" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
        <Radar
          dataKey="value"
          stroke={color}
          fill={color}
          fillOpacity={0.2}
        />
        <Tooltip
          contentStyle={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-primary)',
            fontSize: 12,
          }}
          formatter={(v: number) => [`${v}%`]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
