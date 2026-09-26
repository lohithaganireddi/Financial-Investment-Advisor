import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Coins,
  Newspaper,
  ShieldAlert,
  Briefcase,
  Bot,
  PieChart,
  History,
  Settings,
  X,
  Sparkles,
  LogOut,
  User
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ mobileOpen, setMobileOpen }) {
  const { user, logout } = useAuth();

  const handleNavClick = () => {
    if (mobileOpen && setMobileOpen) {
      setMobileOpen(false);
    }
  };

  const navGroups = [
    {
      title: 'Home',
      items: [
        { label: 'AI Dashboard', path: '/', icon: LayoutDashboard },
      ],
    },
    {
      title: 'Market',
      items: [
        { label: 'Stock Analysis', path: '/stocks', icon: TrendingUp },
        { label: 'Crypto Analysis', path: '/crypto', icon: Coins },
        { label: 'Financial News', path: '/news', icon: Newspaper },
      ],
    },
    {
      title: 'Intelligence',
      items: [
        { label: 'Risk Dashboard', path: '/risk', icon: ShieldAlert },
        { label: 'Portfolio Advisor', path: '/portfolio', icon: Briefcase },
        { label: 'Agent Activity', path: '/agents', icon: Bot },
      ],
    },
    {
      title: 'Insights',
      items: [
        { label: 'Analytics', path: '/analytics', icon: PieChart },
        { label: 'Analysis History', path: '/history', icon: History },
      ],
    },
    {
      title: 'System',
      items: [
        { label: 'Settings', path: '/settings', icon: Settings },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div className="sidebar-backdrop" onClick={() => setMobileOpen(false)} />
      )}

      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="brand-logo-icon">
              <Sparkles size={20} color="#3b82f6" />
            </div>
            <div>
              <div className="sidebar-brand-name">FinSight 2.0</div>
              <div className="sidebar-brand-sub">Multi-Agent AI</div>
            </div>
          </div>
          {setMobileOpen && (
            <button
              className="mobile-close-btn"
              onClick={() => setMobileOpen(false)}
              aria-label="Close navigation"
            >
              <X size={20} />
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          {navGroups.map((group, idx) => (
            <div key={idx} className="nav-group">
              <div className="nav-group-title">{group.title}</div>
              {group.items.map((item) => {
                const IconComponent = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    onClick={handleNavClick}
                  >
                    <IconComponent size={18} className="nav-icon" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {user && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.4rem 0.6rem',
                borderRadius: '6px',
                background: 'rgba(255, 255, 255, 0.03)',
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600, color: 'var(--text-main)' }}>
                <User size={14} color="#60a5fa" />
                {user.username}
              </span>
              <button
                onClick={logout}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#ef4444',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '2px',
                }}
                title="Log Out"
              >
                <LogOut size={14} />
              </button>
            </div>
          )}
          <div className="version-chip">v0.26.0 • Agentic AI</div>
        </div>
      </aside>
    </>
  );
}
