import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  User,
  Sliders,
  Database,
  Info,
  CheckCircle2,
  Lock,
  LogOut,
  Star,
  Plus,
  Trash2,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';

export default function Settings() {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('sf_access_token') || '');
  const [authMode, setAuthMode] = useState('login'); // login or register
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authMsg, setAuthMsg] = useState(null);
  const [authError, setAuthError] = useState(null);

  // Watchlist State
  const [watchlist, setWatchlist] = useState([]);
  const [newAssetType, setNewAssetType] = useState('stock');
  const [newAsset, setNewAsset] = useState('');
  const [newTargetPrice, setNewTargetPrice] = useState('');
  const [newNotes, setNewNotes] = useState('');

  useEffect(() => {
    fetchProfile();
    fetchWatchlist();
  }, [token]);

  const fetchProfile = async () => {
    try {
      const resp = await fetch('/api/auth/me', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.success && data.user) {
          setCurrentUser(data.user);
        }
      }
    } catch (err) {
      console.warn('Could not fetch user profile:', err);
    }
  };

  const fetchWatchlist = async () => {
    try {
      const resp = await fetch('/api/watchlist', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.success && Array.isArray(data.items)) {
          setWatchlist(data.items);
        }
      }
    } catch (err) {
      console.warn('Could not fetch user watchlist:', err);
    }
  };

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthMsg(null);
    setAuthError(null);

    const endpoint = authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
    const payload = authMode === 'register'
      ? { username, email, password }
      : { username, password };

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await resp.json();
      if (!resp.ok) {
        setAuthError(data.detail || 'Authentication failed.');
      } else {
        localStorage.setItem('sf_access_token', data.access_token);
        setToken(data.access_token);
        setCurrentUser(data.user);
        setAuthMsg(authMode === 'register' ? 'Account created successfully!' : 'Logged in successfully!');
        setUsername('');
        setEmail('');
        setPassword('');
      }
    } catch (err) {
      setAuthError(`Authentication error: ${err.message}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('sf_access_token');
    setToken('');
    setCurrentUser(null);
    setWatchlist([]);
    setAuthMsg('Logged out of local session.');
  };

  const handleAddWatchlist = async (e) => {
    e.preventDefault();
    if (!newAsset.trim()) return;

    try {
      const resp = await fetch('/api/watchlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          asset_type: newAssetType,
          asset: newAsset.toUpperCase(),
          target_price: newTargetPrice || null,
          notes: newNotes || null,
        }),
      });

      if (resp.ok) {
        setNewAsset('');
        setNewTargetPrice('');
        setNewNotes('');
        fetchWatchlist();
      }
    } catch (err) {
      console.warn('Failed to add item to watchlist:', err);
    }
  };

  const handleRemoveWatchlist = async (itemId) => {
    try {
      const resp = await fetch(`/api/watchlist/${itemId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (resp.ok) {
        fetchWatchlist();
      }
    } catch (err) {
      console.warn('Failed to remove watchlist item:', err);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <SettingsIcon size={24} color="#94a3b8" />
            User Security, Authentication & Preferences
          </h2>
          <p className="page-subtitle">
            Manage user profiles, JWT authentication tokens, saved watchlists, and database settings.
          </p>
        </div>
      </div>

      <div className="settings-sections">
        {/* User Authentication & Profile Card */}
        <div className="card">
          <div className="card-title" style={{ justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <ShieldCheck size={20} color="#3b82f6" />
              User Authentication & Security Profile
            </div>
            {currentUser && (
              <span className="status-badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontSize: '0.75rem' }}>
                <CheckCircle2 size={12} /> JWT Auth Active
              </span>
            )}
          </div>

          {authMsg && (
            <div className="info-box" style={{ borderColor: 'rgba(16, 185, 129, 0.4)', color: '#34d399', marginBottom: '1rem' }}>
              <CheckCircle2 size={16} /> <span>{authMsg}</span>
            </div>
          )}
          {authError && (
            <div className="info-box" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171', marginBottom: '1rem' }}>
              <AlertCircle size={16} /> <span>{authError}</span>
            </div>
          )}

          {currentUser ? (
            <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div className="form-grid" style={{ marginBottom: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input type="text" className="form-input" value={currentUser.username} readOnly />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input type="text" className="form-input" value={currentUser.email} readOnly />
                </div>
                <div className="form-group">
                  <label className="form-label">Role</label>
                  <input type="text" className="form-input" value={currentUser.role?.toUpperCase()} readOnly />
                </div>
                <div className="form-group">
                  <label className="form-label">User ID</label>
                  <input type="text" className="form-input" value={`#${currentUser.id}`} readOnly />
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="tab-btn"
                style={{ color: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', display: 'inline-flex', alignItems: 'center', gap: 6, padding: '0.4rem 0.9rem' }}
              >
                <LogOut size={14} /> Log Out Session
              </button>
            </div>
          ) : (
            <div>
              <div className="tabs" style={{ marginBottom: '1rem' }}>
                <button
                  className={`tab-btn ${authMode === 'login' ? 'active' : ''}`}
                  onClick={() => setAuthMode('login')}
                >
                  Log In
                </button>
                <button
                  className={`tab-btn ${authMode === 'register' ? 'active' : ''}`}
                  onClick={() => setAuthMode('register')}
                >
                  Register Account
                </button>
              </div>

              <form onSubmit={handleAuthSubmit} className="form-grid">
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-input"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter username"
                    required
                  />
                </div>

                {authMode === 'register' && (
                  <div className="form-group">
                    <label className="form-label">Email Address</label>
                    <input
                      type="email"
                      className="form-input"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="analyst@smartfinance.com"
                      required
                    />
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>

                <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                  <button type="submit" className="btn-primary" style={{ width: '100%', padding: '0.65rem' }}>
                    <Lock size={14} /> {authMode === 'register' ? 'Create Account' : 'Log In'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Saved Portfolio Watchlist Preferences */}
        <div className="card">
          <div className="card-title">
            <Star size={18} color="#f59e0b" />
            Saved Portfolio Watchlist Preferences ({watchlist.length})
          </div>

          <form onSubmit={handleAddWatchlist} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <select
              value={newAssetType}
              onChange={(e) => setNewAssetType(e.target.value)}
              className="form-select"
              style={{ padding: '0.4rem 0.6rem', fontSize: '0.85rem' }}
            >
              <option value="stock">Stock Equity</option>
              <option value="crypto">Cryptocurrency</option>
            </select>

            <input
              type="text"
              placeholder="Ticker (e.g. AAPL, BTC)"
              value={newAsset}
              onChange={(e) => setNewAsset(e.target.value)}
              className="form-input"
              style={{ padding: '0.4rem 0.6rem', fontSize: '0.85rem' }}
              required
            />

            <input
              type="text"
              placeholder="Target Price (Optional)"
              value={newTargetPrice}
              onChange={(e) => setNewTargetPrice(e.target.value)}
              className="form-input"
              style={{ padding: '0.4rem 0.6rem', fontSize: '0.85rem' }}
            />

            <button type="submit" className="btn-primary" style={{ padding: '0.4rem 0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, fontSize: '0.85rem' }}>
              <Plus size={14} /> Add Watchlist
            </button>
          </form>

          {watchlist.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table className="telemetry-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.6rem' }}>Asset</th>
                    <th style={{ padding: '0.6rem' }}>Type</th>
                    <th style={{ padding: '0.6rem' }}>Target Price</th>
                    <th style={{ padding: '0.6rem' }}>Added Date</th>
                    <th style={{ padding: '0.6rem', textAlign: 'right' }}>Remove</th>
                  </tr>
                </thead>
                <tbody>
                  {watchlist.map((item) => (
                    <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.85rem' }}>
                      <td style={{ padding: '0.6rem', fontWeight: 700, color: 'var(--text-main)' }}>{item.asset}</td>
                      <td style={{ padding: '0.6rem', textTransform: 'uppercase', fontSize: '0.75rem', color: '#60a5fa' }}>{item.asset_type}</td>
                      <td style={{ padding: '0.6rem', color: 'var(--text-muted)' }}>{item.target_price || 'None'}</td>
                      <td style={{ padding: '0.6rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.added_at ? new Date(item.added_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td style={{ padding: '0.6rem', textAlign: 'right' }}>
                        <button
                          onClick={() => handleRemoveWatchlist(item.id)}
                          style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', opacity: 0.8 }}
                          title="Remove item"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No saved watchlist items yet. Use the form above to pin your favorite stocks or crypto assets.</p>
          )}
        </div>

        {/* Database & Application Info */}
        <div className="card">
          <div className="card-title">
            <Database size={18} color="#10b981" />
            Database & Telemetry Storage
          </div>
          <div className="info-box">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <CheckCircle2 size={16} color="#10b981" />
              <strong>SQLite Persistence & Auth Schema Active</strong>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              User accounts, JWT security hashes, Watchlist preferences, and `agent_activity` sequence logs are persisted in `smartfinance.db`.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
