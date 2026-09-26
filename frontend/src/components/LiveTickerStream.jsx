import React, { useState, useEffect, useRef } from 'react';
import {
  Radio,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  X,
  RefreshCw,
  Zap
} from 'lucide-react';

export default function LiveTickerStream() {
  const [status, setStatus] = useState('CONNECTING'); // CONNECTING, CONNECTED, DISCONNECTED
  const [tickers, setTickers] = useState({});
  const [newSymbol, setNewSymbol] = useState('');
  const [newAssetType, setNewAssetType] = useState('stock');

  const socketRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    setStatus('CONNECTING');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Fallback to local FastAPI server port 8000 if running Vite dev server
    const host = window.location.port === '5173' || window.location.port === '3000'
      ? '127.0.0.1:8000'
      : window.location.host;

    const wsUrl = `${protocol}//${host}/api/ws/ticker`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setStatus('CONNECTED');
        // Auto-subscribe default baseline tickers
        ws.send(JSON.stringify({ action: 'subscribe', asset_type: 'stock', symbol: 'AAPL' }));
        ws.send(JSON.stringify({ action: 'subscribe', asset_type: 'stock', symbol: 'MSFT' }));
        ws.send(JSON.stringify({ action: 'subscribe', asset_type: 'crypto', symbol: 'bitcoin' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ticker_update' && data.symbol) {
            setTickers((prev) => ({
              ...prev,
              [`${data.asset_type}:${data.symbol}`]: {
                ...data,
                updatedAt: new Date().toLocaleTimeString(),
              },
            }));
          }
        } catch (err) {
          console.warn('WebSocket message parse error:', err);
        }
      };

      ws.onerror = () => {
        setStatus('DISCONNECTED');
      };

      ws.onclose = () => {
        setStatus('DISCONNECTED');
      };
    } catch (err) {
      setStatus('DISCONNECTED');
    }
  };

  const handleAddTicker = (e) => {
    e.preventDefault();
    if (!newSymbol.trim() || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    const cleanSym = newSymbol.trim().toUpperCase();
    socketRef.current.send(
      JSON.stringify({
        action: 'subscribe',
        asset_type: newAssetType,
        symbol: cleanSym,
      })
    );

    setNewSymbol('');
  };

  const handleRemoveTicker = (assetKey) => {
    const [asset_type, symbol] = assetKey.split(':');
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          action: 'unsubscribe',
          asset_type,
          symbol,
        })
      );
    }
    setTickers((prev) => {
      const copy = { ...prev };
      delete copy[assetKey];
      return copy;
    });
  };

  return (
    <div className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 25, 0.9) 100%)', border: '1px solid rgba(59, 130, 246, 0.3)', marginBottom: '1.75rem' }}>
      <div className="card-title" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Radio size={20} color="#3b82f6" />
          Real-Time WebSocket Ticker Streaming Engine
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span
            className="status-badge"
            style={{
              backgroundColor: status === 'CONNECTED' ? 'rgba(16, 185, 129, 0.15)' : status === 'CONNECTING' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: status === 'CONNECTED' ? '#34d399' : status === 'CONNECTING' ? '#fbbf24' : '#f87171',
              border: `1px solid ${status === 'CONNECTED' ? 'rgba(16, 185, 129, 0.4)' : status === 'CONNECTING' ? 'rgba(245, 158, 11, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
              fontSize: '0.75rem',
            }}
          >
            <span
              className="status-dot"
              style={{
                backgroundColor: status === 'CONNECTED' ? '#10b981' : status === 'CONNECTING' ? '#f59e0b' : '#ef4444',
                boxShadow: `0 0 8px ${status === 'CONNECTED' ? '#10b981' : status === 'CONNECTING' ? '#f59e0b' : '#ef4444'}`,
              }}
            />
            {status}
          </span>

          {status === 'DISCONNECTED' && (
            <button
              onClick={connectWebSocket}
              className="tab-btn"
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', color: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.12)' }}
            >
              <RefreshCw size={12} /> Reconnect
            </button>
          )}
        </div>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Live bi-directional streaming broadcast receiving real-time price updates for equities and cryptocurrency assets.
      </p>

      {/* Subscribe Control Form */}
      <form onSubmit={handleAddTicker} style={{ display: 'flex', gap: '0.6rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <select
          value={newAssetType}
          onChange={(e) => setNewAssetType(e.target.value)}
          className="form-select"
          style={{ width: 'auto', padding: '0.35rem 0.6rem', fontSize: '0.85rem' }}
        >
          <option value="stock">Stock</option>
          <option value="crypto">Crypto</option>
        </select>

        <input
          type="text"
          placeholder="Ticker Symbol (e.g. NVDA, ethereum)"
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value)}
          className="form-input"
          style={{ width: '220px', padding: '0.35rem 0.6rem', fontSize: '0.85rem' }}
          required
        />

        <button
          type="submit"
          className="btn-primary"
          disabled={status !== 'CONNECTED'}
          style={{ padding: '0.35rem 0.8rem', display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.85rem' }}
        >
          <Plus size={14} /> Subscribe Live Stream
        </button>
      </form>

      {/* Live Tickers Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.85rem' }}>
        {Object.entries(tickers).map(([key, item]) => {
          const isPositive = item.change_percent >= 0;
          return (
            <div
              key={key}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-color)',
                padding: '0.85rem 1rem',
                borderRadius: '10px',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justify: 'space-between',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Zap size={14} color="#3b82f6" />
                  <strong style={{ fontSize: '1rem', color: 'var(--text-main)' }}>{item.symbol}</strong>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>({item.asset_type})</span>
                </div>
                <button
                  onClick={() => handleRemoveTicker(key)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 2 }}
                  title="Unsubscribe"
                >
                  <X size={14} />
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 4 }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  ${item.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>

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
                  {isPositive ? `+${item.change_percent}%` : `${item.change_percent}%`}
                </span>
              </div>

              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 6, display: 'flex', justifyContent: 'space-between' }}>
                <span>Updated: {item.updatedAt}</span>
                <span style={{ color: item.status === 'ok' ? '#34d399' : '#f59e0b' }}>● {item.status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
