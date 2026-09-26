import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Star,
  Radio,
  ArrowUpRight,
  ArrowDownRight,
  Bot,
  Bell,
  RefreshCw,
  Plus,
  AlertCircle,
  TrendingUp,
  Coins
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useFinancial } from '../context/FinancialContext';

export default function WatchlistWidget() {
  const { token, user } = useAuth();
  const { handleQueryAnalyze, loading: analysisLoading } = useFinancial();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // WebSocket Live Tickers State
  const [wsStatus, setWsStatus] = useState('CONNECTING'); // CONNECTING, CONNECTED, DISCONNECTED
  const [livePrices, setLivePrices] = useState({});
  const socketRef = useRef(null);

  useEffect(() => {
    fetchWatchlist();
  }, [token]);

  useEffect(() => {
    if (items.length > 0) {
      connectWebSocket();
    } else {
      setLoading(false);
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [items]);

  const fetchWatchlist = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch('/api/watchlist', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.success && Array.isArray(data.items)) {
          setItems(data.items);
        }
      } else {
        setError('Could not retrieve user watchlist preferences.');
      }
    } catch (err) {
      setError(`Failed to fetch watchlist: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    setWsStatus('CONNECTING');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.port === '5173' || window.location.port === '3000'
      ? '127.0.0.1:8000'
      : window.location.host;

    const wsUrl = `${protocol}//${host}/api/ws/ticker`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setWsStatus('CONNECTED');
        // Subscribe to all saved watchlist items
        items.forEach((item) => {
          ws.send(
            JSON.stringify({
              action: 'subscribe',
              asset_type: item.asset_type,
              symbol: item.asset,
            })
          );
        });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ticker_update' && data.symbol) {
            setLivePrices((prev) => ({
              ...prev,
              [`${data.asset_type.toLowerCase()}:${data.symbol.toUpperCase()}`]: {
                ...data,
                updatedAt: new Date().toLocaleTimeString(),
              },
            }));
          }
        } catch (err) {
          console.warn('Watchlist WebSocket parse error:', err);
        }
      };

      ws.onerror = () => {
        setWsStatus('DISCONNECTED');
      };

      ws.onclose = () => {
        setWsStatus('DISCONNECTED');
      };
    } catch (err) {
      setWsStatus('DISCONNECTED');
    }
  };

  const handleRunAnalysis = (asset, assetType) => {
    const prompt = assetType === 'crypto' ? `Analyze ${asset} cryptocurrency` : `Analyze ${asset}`;
    handleQueryAnalyze({ query: prompt });
  };

  if (loading) {
    return (
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1.75rem' }}>
        <div className="card-title">
          <Star size={20} color="#f59e0b" />
          Personalized Watchlist Monitoring
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-muted)' }}>
          <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
          <span>Loading saved watchlist items...</span>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          marginBottom: '1.75rem',
        }}
      >
        <div className="card-title" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Star size={20} color="#f59e0b" />
            Personalized Live Watchlist Dashboard
          </div>
          <span className="status-badge" style={{ backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            No Saved Assets
          </span>
        </div>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Welcome, <strong>{user?.username || 'Analyst'}</strong>! You haven't added any stocks or cryptocurrencies to your personal watchlist yet.
        </p>
        <Link
          to="/settings"
          className="btn-primary"
          style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 6, padding: '0.5rem 1rem' }}
        >
          <Plus size={14} /> Add Assets in Settings
        </Link>
      </div>
    );
  }

  return (
    <div
      className="card"
      style={{
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.75) 100%)',
        border: '1px solid rgba(245, 158, 11, 0.35)',
        marginBottom: '1.75rem',
      }}
    >
      {/* Widget Header */}
      <div className="card-title" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Star size={20} color="#f59e0b" />
          Personalized Watchlist Monitoring ({items.length})
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span
            className="status-badge"
            style={{
              backgroundColor: wsStatus === 'CONNECTED' ? 'rgba(16, 185, 129, 0.15)' : wsStatus === 'CONNECTING' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: wsStatus === 'CONNECTED' ? '#34d399' : wsStatus === 'CONNECTING' ? '#fbbf24' : '#f87171',
              border: `1px solid ${wsStatus === 'CONNECTED' ? 'rgba(16, 185, 129, 0.4)' : wsStatus === 'CONNECTING' ? 'rgba(245, 158, 11, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
              fontSize: '0.75rem',
            }}
          >
            <Radio size={12} style={{ marginRight: 4 }} />
            Live Stream: {wsStatus}
          </span>

          {wsStatus === 'DISCONNECTED' && (
            <button
              onClick={connectWebSocket}
              className="tab-btn"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', color: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.12)' }}
            >
              <RefreshCw size={12} /> Reconnect
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="info-box" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171', marginBottom: '1rem' }}>
          <AlertCircle size={16} /> <span>{error}</span>
        </div>
      )}

      {/* Watchlist Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.95rem', marginTop: '0.5rem' }}>
        {items.map((item) => {
          const key = `${item.asset_type.toLowerCase()}:${item.asset.toUpperCase()}`;
          const liveData = livePrices[key];
          const hasLiveData = !!liveData && liveData.price !== undefined;

          // Target Price Alert Logic
          let targetHit = false;
          let targetPriceNum = null;

          if (item.target_price) {
            const parsedTarget = parseFloat(item.target_price.replace(/[^0-9.]/g, ''));
            if (!isNaN(parsedTarget) && parsedTarget > 0) {
              targetPriceNum = parsedTarget;
              if (hasLiveData && liveData.price >= parsedTarget) {
                targetHit = true;
              }
            }
          }

          const isPositive = hasLiveData && liveData.change_percent >= 0;

          return (
            <div
              key={item.id}
              style={{
                background: targetHit ? 'rgba(16, 185, 129, 0.08)' : 'rgba(15, 23, 42, 0.7)',
                border: `1px solid ${targetHit ? 'rgba(16, 185, 129, 0.5)' : 'var(--border-color)'}`,
                borderRadius: '10px',
                padding: '0.9rem 1rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'all 0.2s ease-in-out',
              }}
            >
              <div>
                {/* Item Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    {item.asset_type === 'stock' ? (
                      <TrendingUp size={16} color="#3b82f6" />
                    ) : (
                      <Coins size={16} color="#8b5cf6" />
                    )}
                    <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>{item.asset}</strong>
                    <span
                      style={{
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        padding: '1px 5px',
                        borderRadius: '4px',
                        backgroundColor: item.asset_type === 'stock' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(139, 92, 246, 0.15)',
                        color: item.asset_type === 'stock' ? '#60a5fa' : '#c084fc',
                        textTransform: 'uppercase',
                      }}
                    >
                      {item.asset_type}
                    </span>
                  </div>

                  {targetHit && (
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        color: '#34d399',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 3,
                      }}
                    >
                      <Bell size={10} /> Target Reached
                    </span>
                  )}
                </div>

                {/* Price Display */}
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, margin: '6px 0' }}>
                  <span style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)' }}>
                    {hasLiveData
                      ? `$${liveData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      : 'Fetching...'}
                  </span>

                  {hasLiveData && (
                    <span
                      style={{
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        color: isPositive ? '#10b981' : '#ef4444',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                      }}
                    >
                      {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                      {isPositive ? `+${liveData.change_percent}%` : `${liveData.change_percent}%`}
                    </span>
                  )}
                </div>

                {/* Target Price & Notes */}
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: 2, margin: '4px 0 10px 0' }}>
                  {item.target_price && (
                    <div>Target Price: <strong style={{ color: 'var(--text-main)' }}>{item.target_price}</strong></div>
                  )}
                  {item.notes && <div style={{ fontStyle: 'italic', opacity: 0.85 }}>"{item.notes}"</div>}
                </div>
              </div>

              {/* Action Trigger */}
              <button
                onClick={() => handleRunAnalysis(item.asset, item.asset_type)}
                disabled={analysisLoading}
                className="btn-primary"
                style={{
                  width: '100%',
                  padding: '0.4rem 0.6rem',
                  fontSize: '0.8rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 6,
                  marginTop: '0.5rem',
                }}
              >
                <Bot size={14} /> Run AI Analysis
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
