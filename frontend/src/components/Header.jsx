import React from 'react';
import { Menu, Activity, User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Header({ setMobileOpen }) {
  const { user, logout } = useAuth();

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

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {user && (
          <div
            className="user-badge"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'rgba(59, 130, 246, 0.12)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '20px',
              padding: '0.3rem 0.75rem',
              fontSize: '0.8rem',
              color: '#60a5fa',
              fontWeight: 600,
            }}
          >
            <User size={14} />
            <span>{user.username}</span>
            <button
              onClick={logout}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                marginLeft: '0.25rem',
                padding: '2px',
              }}
              title="Log Out Session"
            >
              <LogOut size={13} />
            </button>
          </div>
        )}

        <div className="status-badge">
          <span className="status-dot"></span>
          <Activity size={14} style={{ marginRight: 4 }} />
          FastAPI & Agents Online
        </div>
      </div>
    </header>
  );
}
