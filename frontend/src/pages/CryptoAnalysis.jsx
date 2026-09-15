import React, { useState } from 'react';
import { Coins, Search, Sparkles, AlertCircle } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import ResultCard from '../components/ResultCard';

export default function CryptoAnalysis() {
  const { result, loading, handleStructuredAnalyze } = useFinancial();
  const [coinId, setCoinId] = useState('bitcoin');
  const [newsQuery, setNewsQuery] = useState('Bitcoin');
  const [errorMsg, setErrorMsg] = useState('');

  const cryptoPresets = [
    { id: 'bitcoin', name: 'Bitcoin', symbol: 'BTC' },
    { id: 'ethereum', name: 'Ethereum', symbol: 'ETH' },
    { id: 'solana', name: 'Solana', symbol: 'SOL' },
    { id: 'dogecoin', name: 'Dogecoin', symbol: 'DOGE' },
    { id: 'cardano', name: 'Cardano', symbol: 'ADA' },
    { id: 'ripple', name: 'XRP / Ripple', symbol: 'XRP' },
    { id: 'binancecoin', name: 'Binance Coin', symbol: 'BNB' },
    { id: 'polygon', name: 'Polygon', symbol: 'MATIC' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleanId = coinId.trim().toLowerCase();
    if (!cleanId) {
      setErrorMsg('Please enter a valid crypto coin ID.');
      return;
    }
    setErrorMsg('');
    handleStructuredAnalyze({
      asset_type: 'crypto',
      asset: cleanId,
      news_query: newsQuery.trim() || cleanId,
    });
  };

  const handleSelectPreset = (p) => {
    setCoinId(p.id);
    setNewsQuery(p.name);
    setErrorMsg('');
  };

  const isCryptoResult = result && (result.asset_type === 'crypto' || result.market_data?.symbol === coinId);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <Coins size={24} color="#8b5cf6" />
            Crypto Analysis
          </h2>
          <p className="page-subtitle">
            Evaluate digital asset prices, market capitalization stats, and crypto market sentiment.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <Sparkles size={18} color="#8b5cf6" />
          Cryptocurrency Search & Preset Selector
        </div>

        {errorMsg && (
          <div className="error-box" style={{ marginBottom: '1rem' }}>
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Crypto Asset ID</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. bitcoin, ethereum, solana"
                value={coinId}
                onChange={(e) => { setCoinId(e.target.value); setErrorMsg(''); }}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">News Search Query</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Bitcoin, Crypto, Web3"
                value={newsQuery}
                onChange={(e) => setNewsQuery(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <div className="preset-bar">
            <span className="preset-label">Supported Crypto Assets:</span>
            {cryptoPresets.map((p) => (
              <button
                key={p.id}
                type="button"
                className={`preset-chip ${coinId.toLowerCase() === p.id ? 'active' : ''}`}
                onClick={() => handleSelectPreset(p)}
              >
                {p.name}
              </button>
            ))}
          </div>

          <button type="submit" className="btn-primary" style={{ backgroundColor: '#8b5cf6' }} disabled={loading}>
            <Search size={18} />
            {loading ? 'Analyzing Crypto Market...' : `Analyze ${coinId.toUpperCase() || 'Crypto'}`}
          </button>
        </form>
      </div>

      {isCryptoResult && !loading && <ResultCard result={result} />}

      {!isCryptoResult && !loading && (
        <div className="card empty-state-card">
          <Coins size={44} color="#8b5cf6" style={{ opacity: 0.6 }} />
          <h3>No Crypto Analysis Loaded</h3>
          <p>
            Select a crypto asset preset above or type a coin ID to execute the crypto intelligence pipeline.
          </p>
        </div>
      )}
    </div>
  );
}
