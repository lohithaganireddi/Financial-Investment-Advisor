import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { FinancialProvider, useFinancial } from './context/FinancialContext';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

import Home from './pages/Home';
import StockAnalysis from './pages/StockAnalysis';
import CryptoAnalysis from './pages/CryptoAnalysis';
import FinancialNews from './pages/FinancialNews';
import RiskDashboard from './pages/RiskDashboard';
import PortfolioAdvisor from './pages/PortfolioAdvisor';
import AgentActivity from './pages/AgentActivity';
import Analytics from './pages/Analytics';
import AnalysisHistory from './pages/AnalysisHistory';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

function MainLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { error, loading } = useFinancial();

  return (
    <div className="app-shell">
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      <div className="main-content-wrapper">
        <Header setMobileOpen={setMobileOpen} />

        {error && (
          <div className="error-box" style={{ margin: '0 1.5rem 1.5rem 1.5rem' }}>
            <div>
              <strong>Service Notice:</strong> {error}
            </div>
          </div>
        )}

        {loading && (
          <div className="card loading-box" style={{ margin: '0 1.5rem 1.5rem 1.5rem' }}>
            <div className="spinner"></div>
            <div>
              <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>
                Executing Autonomous Agent Intelligence Pipeline...
              </strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Sequential execution: Market Data Agent &rarr; News Agent &rarr; Risk Agent &rarr; Portfolio Agent
              </p>
            </div>
          </div>
        )}

        <main className="main-body">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/stocks" element={<StockAnalysis />} />
            <Route path="/crypto" element={<CryptoAnalysis />} />
            <Route path="/news" element={<FinancialNews />} />
            <Route path="/risk" element={<RiskDashboard />} />
            <Route path="/portfolio" element={<PortfolioAdvisor />} />
            <Route path="/agents" element={<AgentActivity />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/history" element={<AnalysisHistory />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <FinancialProvider>
        <MainLayout />
      </FinancialProvider>
    </BrowserRouter>
  );
}