import React from 'react';
import { Settings as SettingsIcon, User, Sliders, Database, Info, CheckCircle2 } from 'lucide-react';

export default function Settings() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <SettingsIcon size={24} color="#94a3b8" />
            System Settings & Preferences
          </h2>
          <p className="page-subtitle">
            Configure UI display options, local SQLite database storage, and agent execution preferences.
          </p>
        </div>
      </div>

      <div className="settings-sections">
        {/* User Profile Overview */}
        <div className="card">
          <div className="card-title">
            <User size={18} color="#3b82f6" />
            User Profile (Local Session)
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Display Name</label>
              <input type="text" className="form-input" defaultValue="Financial Analyst" readOnly />
            </div>
            <div className="form-group">
              <label className="form-label">Role / Permission</label>
              <input type="text" className="form-input" defaultValue="Administrator (Local)" readOnly />
            </div>
          </div>
        </div>

        {/* Application Preferences */}
        <div className="card">
          <div className="card-title">
            <Sliders size={18} color="#8b5cf6" />
            Application Preferences
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">UI Color Theme</label>
              <select className="form-select" defaultValue="dark">
                <option value="dark">Dark Fintech Theme (Active)</option>
                <option value="light" disabled>Light Theme (Coming Soon)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Default History Record Fetch Limit</label>
              <select className="form-select" defaultValue="20">
                <option value="10">10 Records</option>
                <option value="20">20 Records</option>
                <option value="50">50 Records</option>
              </select>
            </div>
          </div>
        </div>

        {/* Local Storage & DB */}
        <div className="card">
          <div className="card-title">
            <Database size={18} color="#10b981" />
            Database & Telemetry Storage
          </div>
          <div className="info-box">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <CheckCircle2 size={16} color="#10b981" />
              <strong>SQLite Persistence Enabled</strong>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Analysis records and step-by-step `agent_activity` sequence logs are stored locally in `smartfinance.db`.
            </p>
          </div>
        </div>

        {/* Platform Info */}
        <div className="card">
          <div className="card-title">
            <Info size={18} color="#06b6d4" />
            About FinSight 2.0
          </div>
          <div className="about-details" style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
            <p><strong>Application:</strong> SmartFinancial Advisor (FinSight 2.0)</p>
            <p><strong>Version:</strong> v0.26.0 (Day 26 Multi-Page Frontend Release)</p>
            <p><strong>Architecture:</strong> Autonomous Multi-Agent AI Engine (StockAgent, CryptoAgent, NewsAgent, RiskAgent, PortfolioAgent)</p>
            <p><strong>Stack:</strong> React 18 + React Router v6 + FastAPI + SQLite + Lucide Icons</p>
          </div>
        </div>
      </div>
    </div>
  );
}
