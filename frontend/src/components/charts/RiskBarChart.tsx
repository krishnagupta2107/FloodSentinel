import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts';
import { riskColor } from '../../utils/risk';
import type { SiteRankOutput } from '../../types/api';

interface RiskBarChartProps {
  sites: SiteRankOutput[];
}

export function RiskBarChart({ sites }: RiskBarChartProps) {
  const data = sites.map(s => ({
    name: s.site_id.replace('SITE_CATCH_', '#'),
    score: parseFloat(((s.composite_risk_score ?? s.risk_score ?? 0) * 100).toFixed(1)),
    level: s.risk_level,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
        <Tooltip
          contentStyle={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-primary)',
            fontSize: 12,
          }}
          formatter={(v: number) => [`${v}%`, 'Risk Score']}
        />
        <Bar dataKey="score" radius={[4, 4, 0, 0]}>
          {data.map((entry, idx) => (
            <Cell key={idx} fill={riskColor(entry.level as any)} fillOpacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
