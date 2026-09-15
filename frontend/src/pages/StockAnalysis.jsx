import React, { useState } from 'react';
import { TrendingUp, Search, Sparkles, AlertCircle } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import ResultCard from '../components/ResultCard';

export default function StockAnalysis() {
  const { result, loading, handleStructuredAnalyze } = useFinancial();
  const [symbol, setSymbol] = useState('AAPL');
  const [newsQuery, setNewsQuery] = useState('Apple');
  const [errorMsg, setErrorMsg] = useState('');

  const stockPresets = [
    { symbol: 'AAPL', name: 'Apple' },
    { symbol: 'MSFT', name: 'Microsoft' },
    { symbol: 'TSLA', name: 'Tesla' },
    { symbol: 'NVDA', name: 'NVIDIA' },
    { symbol: 'GOOGL', name: 'Google' },
    { symbol: 'META', name: 'Meta' },
    { symbol: 'AMZN', name: 'Amazon' },
    { symbol: 'NFLX', name: 'Netflix' },
    { symbol: 'AMD', name: 'AMD' },
    { symbol: 'INTC', name: 'Intel' },
    { symbol: 'KO', name: 'Coca-Cola' },
    { symbol: 'WMT', name: 'Walmart' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleanSym = symbol.trim().toUpperCase();
    if (!cleanSym) {
      setErrorMsg('Please enter a valid stock ticker symbol.');
      return;
    }
    setErrorMsg('');
    handleStructuredAnalyze({
      asset_type: 'stock',
      asset: cleanSym,
      news_query: newsQuery.trim() || cleanSym,
    });
  };

  const handleSelectPreset = (p) => {
    setSymbol(p.symbol);
    setNewsQuery(p.name);
    setErrorMsg('');
  };

  const isStockResult = result && (result.asset_type === 'stock' || result.market_data?.symbol);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <TrendingUp size={24} color="#3b82f6" />
            Stock Analysis
          </h2>
          <p className="page-subtitle">
            Analyze equities with real-time price trends, news sentiment, and volatility risk ratings.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <Sparkles size={18} color="#3b82f6" />
          Equity Search & Preset Selector
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
              <label className="form-label">Stock Symbol / Ticker</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. AAPL, TSLA, NVDA"
                value={symbol}
                onChange={(e) => { setSymbol(e.target.value); setErrorMsg(''); }}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Company / News Keyword</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Apple, Tesla, Tech"
                value={newsQuery}
                onChange={(e) => setNewsQuery(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <div className="preset-bar">
            <span className="preset-label">Supported Stocks:</span>
            {stockPresets.map((p) => (
              <button
                key={p.symbol}
                type="button"
                className={`preset-chip ${symbol.toUpperCase() === p.symbol ? 'active' : ''}`}
                onClick={() => handleSelectPreset(p)}
              >
                {p.symbol}
              </button>
            ))}
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            <Search size={18} />
            {loading ? 'Analyzing Equity Data...' : `Analyze ${symbol.toUpperCase() || 'Stock'}`}
          </button>
        </form>
      </div>

      {isStockResult && !loading && <ResultCard result={result} />}

      {!isStockResult && !loading && (
        <div className="card empty-state-card">
          <TrendingUp size={44} color="#3b82f6" style={{ opacity: 0.6 }} />
          <h3>No Stock Analysis Loaded</h3>
          <p>
            Select a ticker preset above or enter a stock symbol to run the multi-agent stock analysis pipeline.
          </p>
        </div>
      )}
    </div>
  );
}
