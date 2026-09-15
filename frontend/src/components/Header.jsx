import React from 'react';
import { Menu, Activity } from 'lucide-react';

export default function Header({ setMobileOpen }) {
  return (
    <header className="header">
      <div className="header-left">
        {setMobileOpen && (
          <button
            className="mobile-toggle-btn"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation menu"
          >
            <Menu size={22} />
          </button>
        )}
        <div>
          <h1 className="brand-title">SmartFinancial Advisor</h1>
          <div className="brand-subtitle">
            FinSight 2.0 — Multi-Agent Financial Intelligence Platform
          </div>
        </div>
      </div>
      <div className="status-badge">
        <span className="status-dot"></span>
        <Activity size={14} style={{ marginRight: 4 }} />
        FastAPI & Agents Online
      </div>
    </header>
  );
}
