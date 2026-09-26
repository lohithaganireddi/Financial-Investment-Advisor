import React, { useState, useMemo } from 'react';
import {
  PieChart,
  Activity,
  TrendingUp,
  Coins,
  Newspaper,
  ShieldAlert,
  Search,
  Filter,
  BarChart3,
  Award,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  CheckCircle2,
  Info
} from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';

export default function Analytics() {
  const { history, result, analysisContext, handleSelectHistoryRecord } = useFinancial();

  // Filter States
  const [assetFilter, setAssetFilter] = useState('ALL'); // ALL, stock, crypto, news
  const [recFilter, setRecFilter] = useState('ALL'); // ALL, BUY, HOLD, AVOID
  const [riskFilter, setRiskFilter] = useState('ALL'); // ALL, low, medium, high
  const [searchQuery, setSearchQuery] = useState('');

  // Overall Statistics
  const totalAnalyses = history.length;

  const stockCount = history.filter((item) => item.asset_type === 'stock').length;
  const cryptoCount = history.filter((item) => item.asset_type === 'crypto').length;
  const newsCount = history.filter((item) => item.intent === 'GENERAL_FINANCIAL_NEWS' || (!item.asset_type && item.news_query)).length;

  const buyCount = history.filter((item) => item.recommendation?.toUpperCase() === 'BUY').length;
  const holdCount = history.filter((item) => item.recommendation?.toUpperCase() === 'HOLD').length;
  const avoidCount = history.filter((item) => item.recommendation?.toUpperCase() === 'AVOID').length;

  const lowRiskCount = history.filter((item) => item.risk_level?.toLowerCase() === 'low').length;
  const medRiskCount = history.filter((item) => item.risk_level?.toLowerCase() === 'medium').length;
  const highRiskCount = history.filter((item) => item.risk_level?.toLowerCase() === 'high').length;

  const highConfCount = history.filter((item) => item.confidence?.toLowerCase() === 'high').length;
  const medConfCount = history.filter((item) => item.confidence?.toLowerCase() === 'medium').length;
  const lowConfCount = history.filter((item) => item.confidence?.toLowerCase() === 'low').length;

  // Numerical Averages
  const avgRecScore = useMemo(() => {
    const scores = history.map((item) => item.recommendation_score).filter((s) => typeof s === 'number');
    if (scores.length === 0) return null;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  }, [history]);

  const avgRiskScore = useMemo(() => {
    const scores = history.map((item) => item.risk_score).filter((s) => typeof s === 'number');
    if (scores.length === 0) return null;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  }, [history]);

  // Filtered History for Interactive Table
  const filteredHistory = useMemo(() => {
    return history.filter((item) => {
      // Asset Type Filter
      if (assetFilter === 'stock' && item.asset_type !== 'stock') return false;
      if (assetFilter === 'crypto' && item.asset_type !== 'crypto') return false;
      if (assetFilter === 'news' && item.intent !== 'GENERAL_FINANCIAL_NEWS' && item.asset_type) return false;

      // Recommendation Filter
      if (recFilter !== 'ALL' && item.recommendation?.toUpperCase() !== recFilter) return false;

      // Risk Filter
      if (riskFilter !== 'ALL' && item.risk_level?.toLowerCase() !== riskFilter.toLowerCase()) return false;

      // Search Query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const assetMatch = item.asset?.toLowerCase().includes(q);
        const queryMatch = item.query?.toLowerCase().includes(q);
        const recMatch = item.recommendation?.toLowerCase().includes(q);
        if (!assetMatch && !queryMatch && !recMatch) return false;
      }

      return true;
    });
  }, [history, assetFilter, recFilter, riskFilter, searchQuery]);

  // Helper Badge Colors
  const getRecBadgeClass = (rec) => {
    switch (rec?.toUpperCase()) {
      case 'BUY': return 'rec-buy';
      case 'HOLD': return 'rec-hold';
      case 'AVOID': return 'rec-avoid';
      default: return '';
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#94a3b8';
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <PieChart size={24} color="#a855f7" />
            Advanced Portfolio Analytics & Risk Visualizer
          </h2>
          <p className="page-subtitle">
            Interactive multi-agent asset allocation, risk distribution, and confidence breakdown analytics.
          </p>
        </div>
      </div>

      {/* Summary KPI Cards Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Executed Analyses</div>
          <div className="metric-value">{totalAnalyses}</div>
          <div className="metric-sub">SQLite Database Records</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Stock vs Crypto Split</div>
          <div className="metric-value" style={{ fontSize: '1.35rem' }}>
            <span style={{ color: '#3b82f6' }}>{stockCount} Stock</span> / <span style={{ color: '#8b5cf6' }}>{cryptoCount} Crypto</span>
          </div>
          <div className="metric-sub">Equities vs Digital Assets</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Avg Portfolio Score</div>
          <div className="metric-value" style={{ color: avgRecScore !== null && avgRecScore >= 70 ? '#10b981' : '#f59e0b' }}>
            {avgRecScore !== null ? `${avgRecScore} / 100` : 'N/A'}
          </div>
          <div className="metric-sub">Recommendation Score Average</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Avg Risk Score</div>
          <div className="metric-value" style={{ color: avgRiskScore !== null && avgRiskScore <= 35 ? '#10b981' : avgRiskScore > 65 ? '#ef4444' : '#f59e0b' }}>
            {avgRiskScore !== null ? `${avgRiskScore} / 100` : 'N/A'}
          </div>
          <div className="metric-sub">Volatility Index Average</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">High Confidence Ratio</div>
          <div className="metric-value" style={{ color: '#a855f7' }}>
            {totalAnalyses > 0 ? `${Math.round((highConfCount / totalAnalyses) * 100)}%` : '0%'}
          </div>
          <div className="metric-sub">{highConfCount} High • {medConfCount} Med • {lowConfCount} Low</div>
        </div>
      </div>

      {/* Active Synthesis Score Composition Widget (if result is active) */}
      {analysisContext && result?.recommendation?.recommendation_score !== undefined && (
        <div className="card" style={{ background: 'linear-gradient(135deg, rgba(21, 29, 48, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
          <div className="card-title">
            <Layers size={18} color="#a855f7" />
            Active Portfolio Score Composition: {analysisContext.asset || result.asset}
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Deterministic score synthesis calculated from Market Direction, Volatility Risk, and Financial News signals.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
            <div className="hero-metric-box">
              <div className="hero-metric-label">Base Score</div>
              <div className="hero-metric-val" style={{ color: '#94a3b8' }}>50</div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>Starting Score</div>
            </div>

            <div className="hero-metric-box">
              <div className="hero-metric-label">Market Direction</div>
              <div className="hero-metric-val" style={{ color: result.market_data?.market_direction === 'bullish' ? '#10b981' : result.market_data?.market_direction === 'bearish' ? '#ef4444' : '#f59e0b' }}>
                {result.market_data?.market_direction === 'bullish' ? '+20' : result.market_data?.market_direction === 'bearish' ? '-20' : '0'}
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>{result.market_data?.market_direction?.toUpperCase() || 'NEUTRAL'}</div>
            </div>

            <div className="hero-metric-box">
              <div className="hero-metric-label">Risk Level Signal</div>
              <div className="hero-metric-val" style={{ color: result.risk_data?.risk_level === 'low' ? '#10b981' : result.risk_data?.risk_level === 'high' ? '#ef4444' : '#f59e0b' }}>
                {result.risk_data?.risk_level === 'low' ? '+15' : result.risk_data?.risk_level === 'high' ? '-20' : '0'}
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>{result.risk_data?.risk_level?.toUpperCase() || 'MEDIUM'} RISK</div>
            </div>

            <div className="hero-metric-box">
              <div className="hero-metric-label">News Sentiment</div>
              <div className="hero-metric-val" style={{ color: result.news_data?.overall_sentiment === 'positive' ? '#10b981' : result.news_data?.overall_sentiment === 'negative' ? '#ef4444' : '#f59e0b' }}>
                {result.news_data?.overall_sentiment === 'positive' ? '+15' : result.news_data?.overall_sentiment === 'negative' ? '-15' : '0'}
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>{result.news_data?.overall_sentiment?.toUpperCase() || 'NEUTRAL'}</div>
            </div>

            <div className="hero-metric-box" style={{ borderColor: 'rgba(168, 85, 247, 0.5)', background: 'rgba(168, 85, 247, 0.1)' }}>
              <div className="hero-metric-label" style={{ color: '#a855f7', fontWeight: 700 }}>Final Score</div>
              <div className="hero-metric-val" style={{ color: '#a855f7' }}>
                {result.recommendation.recommendation_score} <span style={{ fontSize: '0.75rem' }}>/ 100</span>
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4, fontWeight: 700, color: '#34d399' }}>
                {result.recommendation.recommendation?.toUpperCase()} ({result.recommendation.confidence?.toUpperCase()})
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Segmented Allocation Visualizer */}
      <div className="card">
        <div className="card-title">
          <BarChart3 size={18} color="#3b82f6" />
          Interactive Asset Allocation Visualizer
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Visual proportions of portfolio queries across Equities (Stock), Digital Assets (Crypto), and Financial News.
        </p>

        {/* Multi-segment distribution bar */}
        <div style={{ display: 'flex', height: '18px', borderRadius: '8px', overflow: 'hidden', backgroundColor: 'rgba(255,255,255,0.05)', marginBottom: '1rem' }}>
          <div
            title={`Stock: ${stockCount}`}
            style={{ width: `${totalAnalyses > 0 ? (stockCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#3b82f6', transition: 'width 0.3s' }}
          />
          <div
            title={`Crypto: ${cryptoCount}`}
            style={{ width: `${totalAnalyses > 0 ? (cryptoCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#8b5cf6', transition: 'width 0.3s' }}
          />
          <div
            title={`News: ${newsCount}`}
            style={{ width: `${totalAnalyses > 0 ? (newsCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#10b981', transition: 'width 0.3s' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }} onClick={() => setAssetFilter('stock')}>
            <span style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: '#3b82f6', display: 'inline-block' }} />
            <span>Stock Analyses: <strong>{stockCount}</strong> ({totalAnalyses > 0 ? Math.round((stockCount / totalAnalyses) * 100) : 0}%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }} onClick={() => setAssetFilter('crypto')}>
            <span style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: '#8b5cf6', display: 'inline-block' }} />
            <span>Crypto Analyses: <strong>{cryptoCount}</strong> ({totalAnalyses > 0 ? Math.round((cryptoCount / totalAnalyses) * 100) : 0}%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }} onClick={() => setAssetFilter('news')}>
            <span style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: '#10b981', display: 'inline-block' }} />
            <span>Financial News Queries: <strong>{newsCount}</strong> ({totalAnalyses > 0 ? Math.round((newsCount / totalAnalyses) * 100) : 0}%)</span>
          </div>
        </div>
      </div>

      {/* Breakdown Grids */}
      <div className="grid-2-col">
        {/* Recommendation Ratio Spectrum */}
        <div className="card">
          <div className="card-title">
            <Award size={18} color="#10b981" />
            Recommendation Distribution
          </div>
          <div className="analytics-bar-group">
            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#10b981', fontWeight: 600 }}>BUY Recommendation</span>
                <strong>{buyCount} ({totalAnalyses > 0 ? Math.round((buyCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (buyCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#10b981' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#f59e0b', fontWeight: 600 }}>HOLD Recommendation</span>
                <strong>{holdCount} ({totalAnalyses > 0 ? Math.round((holdCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (holdCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#f59e0b' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#ef4444', fontWeight: 600 }}>AVOID Recommendation</span>
                <strong>{avoidCount} ({totalAnalyses > 0 ? Math.round((avoidCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (avoidCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#ef4444' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Risk Level Volatility Spectrum */}
        <div className="card">
          <div className="card-title">
            <ShieldAlert size={18} color="#f59e0b" />
            Risk Level Distribution Spectrum
          </div>
          <div className="analytics-bar-group">
            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#10b981', fontWeight: 600 }}>Low Volatility Risk</span>
                <strong>{lowRiskCount} ({totalAnalyses > 0 ? Math.round((lowRiskCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (lowRiskCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#10b981' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#f59e0b', fontWeight: 600 }}>Medium Volatility Risk</span>
                <strong>{medRiskCount} ({totalAnalyses > 0 ? Math.round((medRiskCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (medRiskCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#f59e0b' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#ef4444', fontWeight: 600 }}>High Volatility Risk</span>
                <strong>{highRiskCount} ({totalAnalyses > 0 ? Math.round((highRiskCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (highRiskCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#ef4444' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Portfolio Data Table & Filter Controls */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div className="card-title" style={{ marginBottom: 0 }}>
            <Filter size={18} color="#a855f7" />
            Historical Asset Portfolio Breakdown ({filteredHistory.length})
          </div>

          {/* Search Box */}
          <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.4rem 0.75rem', gap: 8, width: '220px' }}>
            <Search size={14} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search ticker/query..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', fontSize: '0.85rem', outline: 'none', width: '100%' }}
            />
          </div>
        </div>

        {/* Filter Controls Row */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.25rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
          {/* Asset Filter Pills */}
          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: 4 }}>Asset:</span>
            {['ALL', 'stock', 'crypto'].map((type) => (
              <button
                key={type}
                className={`tab-btn ${assetFilter === type ? 'active' : ''}`}
                onClick={() => setAssetFilter(type)}
                style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}
              >
                {type.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Recommendation Filter Pills */}
          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: 4 }}>Rec:</span>
            {['ALL', 'BUY', 'HOLD', 'AVOID'].map((rec) => (
              <button
                key={rec}
                className={`tab-btn ${recFilter === rec ? 'active' : ''}`}
                onClick={() => setRecFilter(rec)}
                style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}
              >
                {rec}
              </button>
            ))}
          </div>

          {/* Risk Filter Pills */}
          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: 4 }}>Risk:</span>
            {['ALL', 'low', 'medium', 'high'].map((level) => (
              <button
                key={level}
                className={`tab-btn ${riskFilter === level ? 'active' : ''}`}
                onClick={() => setRiskFilter(level)}
                style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}
              >
                {level.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Data Table */}
        {filteredHistory.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="telemetry-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>ID</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Asset</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Type</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Recommendation</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Rec Score</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Risk Score / Level</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Confidence</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Created At</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map((item) => {
                  const riskColor = getRiskColor(item.risk_level);
                  return (
                    <tr
                      key={item.id}
                      style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', fontSize: '0.85rem' }}
                    >
                      <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-muted)' }}>#{item.id}</td>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {item.asset || 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span style={{
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          backgroundColor: item.asset_type === 'stock' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(139, 92, 246, 0.15)',
                          color: item.asset_type === 'stock' ? '#60a5fa' : '#c084fc',
                          textTransform: 'uppercase'
                        }}>
                          {item.asset_type || 'N/A'}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span className={`recommendation-badge ${getRecBadgeClass(item.recommendation)}`} style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>
                          {item.recommendation?.toUpperCase() || 'N/A'}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700 }}>
                        {item.recommendation_score ?? '-'} / 100
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span style={{ color: riskColor, fontWeight: 600 }}>
                          {item.risk_score ?? '-'} ({item.risk_level?.toUpperCase() || 'N/A'})
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', textTransform: 'uppercase', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        {item.confidence || 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>
                        <button
                          onClick={() => handleSelectHistoryRecord(item.id)}
                          className="tab-btn"
                          style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', color: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            <Info size={32} style={{ opacity: 0.5, marginBottom: '0.5rem' }} />
            <p>No analysis records match the selected filter criteria.</p>
          </div>
        )}
      </div>

      {totalAnalyses === 0 && (
        <div className="card empty-state-card">
          <PieChart size={44} color="#a855f7" style={{ opacity: 0.6 }} />
          <h3>No Analytics History Recorded Yet</h3>
          <p>
            Run financial queries from Stock or Crypto pages to populate execution statistics and historical allocation graphs.
          </p>
        </div>
      )}
    </div>
  );
}
