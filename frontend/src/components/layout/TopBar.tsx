import { RefreshCw, Menu } from 'lucide-react';
import type { ApiStatus, HealthResponse } from '../../types/api';

interface TopBarProps {
  title: string;
  subtitle?: string;
  status: ApiStatus;
  health: HealthResponse | null;
  onRetry?: () => void;
  onOpenMobile?: () => void;
}

export function TopBar({
  title,
  subtitle,
  status,
  health,
  onRetry,
  onOpenMobile,
}: TopBarProps) {
  return (
    <header className="topbar">
      <div className="flex items-center gap-3">
        {onOpenMobile && (
          <button
            type="button"
            className="mobile-menu-btn"
            onClick={onOpenMobile}
            aria-label="Open navigation menu"
          >
            <Menu size={20} />
          </button>
        )}
        <div>
          <div className="topbar-title">{title}</div>
          {subtitle && <div className="topbar-sub">{subtitle}</div>}
        </div>
      </div>

      <div className="topbar-right">
        {health && (
          <div className="hidden sm:flex gap-1.5">
            <ModelPill label="Rainfall" ready={health.models.rainfall} />
            <ModelPill label="Overflow" ready={health.models.overflow} />
            <ModelPill label="Fusion"   ready={health.models.fusion}   />
          </div>
        )}

        <div className={`status-pill ${status}`}>
          <span className="status-dot" />
          {status === 'connecting' ? 'Connecting' : status === 'online' ? 'API Online' : 'API Offline'}
        </div>

        {status === 'offline' && onRetry && (
          <button
            type="button"
            className="btn btn-ghost"
            onClick={onRetry}
            title="Retry connection"
            style={{ padding: '6px 10px' }}
          >
            <RefreshCw size={13} />
          </button>
        )}

        <div style={{ fontSize: 12, color: 'var(--text-muted)', fontVariantNumeric: 'tabular-nums' }}>
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </header>
  );
}

function ModelPill({ label, ready }: { label: string; ready: boolean }) {
  return (
    <span
      style={{
        fontSize: 10,
        fontWeight: 600,
        padding: '2px 7px',
        borderRadius: 4,
        border: '1px solid',
        background: ready ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
        color: ready ? '#22c55e' : '#ef4444',
        borderColor: ready ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)',
        textTransform: 'uppercase' as const,
        letterSpacing: '0.06em',
      }}
    >
      {label}
    </span>
  );
}
