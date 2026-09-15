import React from 'react';
import { TrendingUp, ShieldCheck } from 'lucide-react';

export default function Header() {
  return (
    <header className="header">
      <div>
        <div className="brand-title">SmartFinancial Advisor</div>
        <div className="brand-subtitle">
          FinSight 2.0 — Multi-Agent Financial Intelligence Platform
        </div>
      </div>
      <div className="status-badge">
        <span className="status-dot"></span>
        FastAPI & Agents Online
      </div>
    </header>
  );
}
