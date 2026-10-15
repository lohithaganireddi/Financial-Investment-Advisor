import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authenticatedFetch } from '../services/apiClient';
import {
  Settings as SettingsIcon,
  Database,
  CheckCircle2,
  LogOut,
  Star,
  Plus,
  Trash2,
  ShieldCheck,
  User as UserIcon
} from 'lucide-react';

export default function Settings() {
  const { user: currentUser, token, logout, logoutAll } = useAuth();

  // Watchlist State
  const [watchlist, setWatchlist] = useState([]);
  const [newAssetType, setNewAssetType] = useState('stock');
  const [newAsset, setNewAsset] = useState('');
  const [newTargetPrice, setNewTargetPrice] = useState('');
  const [newNotes, setNewNotes] = useState('');

  useEffect(() => {
    fetchWatchlist();
  }, [token]);

  const fetchWatchlist = async () => {
    try {
      const resp = await authenticatedFetch('/api/watchlist');
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

  const handleAddWatchlist = async (e) => {
    e.preventDefault();
    if (!newAsset.trim()) return;

    try {
      const resp = await authenticatedFetch('/api/watchlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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
      const resp = await authenticatedFetch(`/api/watchlist/${itemId}`, {
        method: 'DELETE',
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
              User Security & Profile Information
            </div>
            {currentUser && (
              <span className="status-badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontSize: '0.75rem' }}>
                <CheckCircle2 size={12} /> JWT Auth Session Active
              </span>
            )}
          </div>

          {currentUser ? (
            <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div className="form-grid" style={{ marginBottom: '1.25rem' }}>
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input type="text" className="form-input" value={currentUser.username || ''} readOnly />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input type="text" className="form-input" value={currentUser.email || 'N/A'} readOnly />
                </div>
                <div className="form-group">
                  <label className="form-label">Role</label>
                  <input type="text" className="form-input" value={(currentUser.role || 'ANALYST').toUpperCase()} readOnly />
                </div>
                <div className="form-group">
                  <label className="form-label">User ID</label>
                  <input type="text" className="form-input" value={`#${currentUser.id}`} readOnly />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button
                  onClick={logout}
                  className="tab-btn"
                  style={{ color: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', display: 'inline-flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', cursor: 'pointer' }}
                >
                  <LogOut size={14} /> Log Out Active Session
                </button>
                <button
                  onClick={logoutAll}
                  className="tab-btn"
                  style={{ color: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.1)', display: 'inline-flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem', cursor: 'pointer' }}
                  title="Revoke all active sessions across all devices"
                >
                  <LogOut size={14} /> Log Out All Sessions / Devices
                </button>
              </div>
            </div>
          ) : (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No active user session detected.</p>
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
