import { AlertTriangle } from 'lucide-react';

interface DemoBannerProps {
  message?: string;
}

export function DemoBanner({ message }: DemoBannerProps) {
  return (
    <div className="demo-banner">
      <AlertTriangle size={14} />
      <strong>DEMO MODE</strong>
      {' — '}
      {message ?? 'Simulation data shown — not live municipal telemetry. Site IDs, coordinates, and sensor readings are synthetic.'}
    </div>
  );
}
