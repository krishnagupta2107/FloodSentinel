import { useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';
import { OverviewPage } from './pages/OverviewPage';
import { SitesPage } from './pages/SitesPage';
import { AlertsPage } from './pages/AlertsPage';
import { FusionPage } from './pages/FusionPage';
import { RainfallPage } from './pages/RainfallPage';
import { OverflowPage } from './pages/OverflowPage';
import { DemoPage } from './pages/DemoPage';
import { AboutPage } from './pages/AboutPage';
import { useApiHealth } from './hooks/useApiHealth';

const ROUTE_INFO: Record<string, { title: string; subtitle: string }> = {
  '/': {
    title: 'Flood Risk Overview',
    subtitle: 'Municipal command center & multi-modal risk priority',
  },
  '/sites': {
    title: 'Catchment Sites Directory',
    subtitle: 'Drainage network monitoring nodes & telemetry inventory',
  },
  '/alerts': {
    title: 'Emergency Alerts & Dispatch',
    subtitle: 'Prioritized high-severity risk events & field protocol',
  },
  '/fusion': {
    title: 'Multi-Modal Risk Fusion',
    subtitle: 'Model 1 (YOLO) + Model 2 (Overflow) + Model 3 (Rainfall) composite ranking',
  },
  '/rainfall': {
    title: 'Rainfall Forecasting',
    subtitle: 'Model 3 — Subdivision-aware LSTM + XGBoost ensemble inference',
  },
  '/overflow': {
    title: 'Overflow Onset Prediction',
    subtitle: 'Model 2 — XGBoost sensor telemetry classification',
  },
  '/demo': {
    title: 'Demo Simulation Sandbox',
    subtitle: 'Synthetic 10-site multi-modal scenario evaluation',
  },
  '/about': {
    title: 'System Architecture & Provenance',
    subtitle: 'Hydrological ML models, technical specs, and operational boundaries',
  },
};

export function App() {
  const { status, health, retry } = useApiHealth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const currentInfo = ROUTE_INFO[location.pathname] ?? {
    title: 'FloodSentinel',
    subtitle: 'Urban Flood Risk Intelligence',
  };

  return (
    <div className="app-shell">
      <Sidebar
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <div className="main-content">
        <TopBar
          title={currentInfo.title}
          subtitle={currentInfo.subtitle}
          status={status}
          health={health}
          onRetry={retry}
          onOpenMobile={() => setMobileOpen(true)}
        />

        <main className="content-body">
          <Routes>
            <Route path="/" element={<OverviewPage status={status} health={health} onRetry={retry} />} />
            <Route path="/sites" element={<SitesPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/fusion" element={<FusionPage />} />
            <Route path="/rainfall" element={<RainfallPage />} />
            <Route path="/overflow" element={<OverflowPage />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<OverviewPage status={status} health={health} onRetry={retry} />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
