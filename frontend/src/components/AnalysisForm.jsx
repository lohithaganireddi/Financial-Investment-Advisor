import React, { useState } from 'react';
import { Search, Sparkles, AlertCircle } from 'lucide-react';

export default function AnalysisForm({ onAnalyze, onQuery, loading }) {
  const [activeTab, setActiveTab] = useState('structured');

  // Structured mode state
  const [assetType, setAssetType] = useState('stock');
  const [asset, setAsset] = useState('AAPL');
  const [newsQuery, setNewsQuery] = useState('Apple');
  const [validationError, setValidationError] = useState('');

  // Natural query mode state
  const [queryText, setQueryText] = useState('Should I invest in Apple?');

  const handleStructuredSubmit = (e) => {
    e.preventDefault();
    setValidationError('');

    const cleanAsset = asset.trim();
    if (!cleanAsset) {
      setValidationError('Please enter a valid asset symbol or coin ID.');
      return;
    }

    onAnalyze({
      asset_type: assetType,
      asset: cleanAsset,
      news_query: newsQuery.trim() || 'finance',
    });
  };

  const handleQuerySubmit = (e) => {
    e.preventDefault();
    setValidationError('');

    const cleanQuery = queryText.trim();
    if (!cleanQuery) {
      setValidationError('Please enter a financial query string.');
      return;
    }

    onQuery({ query: cleanQuery });
  };

  const handlePresetSelect = (symbol, newsName, type = 'stock') => {
    setValidationError('');
    setAssetType(type);
    setAsset(symbol);
    setNewsQuery(newsName);
  };

  return (
    <div className="card">
      <div className="card-title">
        <Sparkles size={20} color="#3b82f6" />
        Execute Financial Intelligence Pipeline
      </div>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'structured' ? 'active' : ''}`}
          onClick={() => { setActiveTab('structured'); setValidationError(''); }}
          type="button"
        >
          Structured Asset Analysis
        </button>
        <button
          className={`tab-btn ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => { setActiveTab('query'); setValidationError(''); }}
          type="button"
        >
          Natural Language Query
        </button>
      </div>

      {validationError && (
        <div className="error-box" style={{ marginBottom: '1rem', padding: '0.75rem 1rem' }}>
          <AlertCircle size={18} />
          <span>{validationError}</span>
        </div>
      )}

      {activeTab === 'structured' ? (
        <form onSubmit={handleStructuredSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Asset Type</label>
              <select
                className="form-select"
                value={assetType}
                onChange={(e) => {
                  const val = e.target.value;
                  setAssetType(val);
                  setValidationError('');
                  if (val === 'stock' && asset === 'bitcoin') {
                    setAsset('AAPL');
                    setNewsQuery('Apple');
                  } else if (val === 'crypto' && asset === 'AAPL') {
                    setAsset('bitcoin');
                    setNewsQuery('Bitcoin');
                  }
                }}
                disabled={loading}
              >
                <option value="stock">Stock (Equities)</option>
                <option value="crypto">Cryptocurrency</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Asset Identifier</label>
              <input
                type="text"
                className="form-input"
                placeholder={assetType === 'stock' ? 'e.g. AAPL, TSLA, MSFT' : 'e.g. bitcoin, ethereum, solana'}
                value={asset}
                onChange={(e) => { setAsset(e.target.value); setValidationError(''); }}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">News Search Query</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. finance, Apple"
                value={newsQuery}
                onChange={(e) => setNewsQuery(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          {/* Preset Chips */}
          <div className="preset-bar">
            <span className="preset-label">Quick Presets:</span>
            {assetType === 'stock' ? (
              <>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('AAPL', 'Apple', 'stock')}>AAPL</button>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('MSFT', 'Microsoft', 'stock')}>MSFT</button>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('TSLA', 'Tesla', 'stock')}>TSLA</button>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('NVDA', 'NVIDIA', 'stock')}>NVDA</button>
              </>
            ) : (
              <>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('bitcoin', 'Bitcoin', 'crypto')}>Bitcoin</button>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('ethereum', 'Ethereum', 'crypto')}>Ethereum</button>
                <button type="button" className="preset-chip" onClick={() => handlePresetSelect('solana', 'Solana', 'crypto')}>Solana</button>
              </>
            )}
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            <Search size={18} />
            {loading ? 'Executing Multi-Agent Pipeline...' : 'Run Financial Analysis'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleQuerySubmit}>
          <div className="form-group" style={{ marginBottom: '1.25rem' }}>
            <label className="form-label">Ask a Financial Query</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Should I invest in Apple? or Analyze Bitcoin"
              value={queryText}
              onChange={(e) => { setQueryText(e.target.value); setValidationError(''); }}
              disabled={loading}
              required
            />
          </div>

          {/* Preset Queries */}
          <div className="preset-bar">
            <span className="preset-label">Example Queries:</span>
            <button type="button" className="preset-chip" onClick={() => setQueryText('Should I invest in Apple?')}>Should I invest in Apple?</button>
            <button type="button" className="preset-chip" onClick={() => setQueryText('Analyze Bitcoin')}>Analyze Bitcoin</button>
            <button type="button" className="preset-chip" onClick={() => setQueryText('Is Tesla risky?')}>Is Tesla risky?</button>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            <Sparkles size={18} />
            {loading ? 'Interpreting Query & Analyzing...' : 'Interpret Query & Run Pipeline'}
          </button>
        </form>
      )}
    </div>
  );
}