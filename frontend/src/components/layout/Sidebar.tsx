import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Layers, ShieldAlert, Activity,
  CloudRain, Waves, FlaskConical, Info, X
} from 'lucide-react';

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

const navItems = [
  { label: 'Overview', to: '/', icon: LayoutDashboard },
  { label: 'Catchment Sites', to: '/sites', icon: Layers },
  { label: 'Incident Alerts', to: '/alerts', icon: ShieldAlert },
  { label: 'Risk Fusion', to: '/fusion', icon: Activity },
  { label: 'Rainfall Forecast', to: '/rainfall', icon: CloudRain },
  { label: 'Overflow Predict', to: '/overflow', icon: Waves },
  { label: 'Demo Simulation', to: '/demo', icon: FlaskConical },
  { label: 'Architecture & About', to: '/about', icon: Info },
];

export function Sidebar({ mobileOpen = false, onCloseMobile }: SidebarProps) {
  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="sidebar-backdrop"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <svg width="20" height="20" viewBox="0 0 32 32" fill="none">
              <path d="M16 4C11 4 7 9 7 14c0 6 9 14 9 14s9-8 9-14c0-5-4-10-9-10z" fill="white" fillOpacity="0.9"/>
              <path d="M9 22c2-1 3.5 1 5.5 0s3-2 5-1 2.5 1.5 3.5 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.7"/>
            </svg>
          </div>
          <div className="sidebar-logo-text">
            <strong>FloodSentinel</strong>
            <span>Risk Intelligence</span>
          </div>
          {mobileOpen && (
            <button
              type="button"
              className="mobile-close-btn"
              onClick={onCloseMobile}
              aria-label="Close navigation"
            >
              <X size={18} />
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">Command Center</div>
          {navItems.map(({ label, to, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
              onClick={onCloseMobile}
            >
              <Icon className="nav-icon" size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div style={{ fontSize: 10, marginBottom: 4, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>
            ML INFERENCE PIPELINE
          </div>
          <div className="text-[11px] text-secondary font-mono">YOLOv8 · XGBoost · LSTM</div>
          <div style={{ marginTop: 4, fontSize: 11, color: 'var(--text-muted)' }}>Multi-Modal Risk Fusion</div>
        </div>
      </aside>
    </>
  );
}
