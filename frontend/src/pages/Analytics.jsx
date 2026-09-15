import React from 'react';
import { PieChart, Activity, TrendingUp, Coins, Newspaper, ShieldAlert, Briefcase } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';

export default function Analytics() {
  const { history } = useFinancial();

  const totalAnalyses = history.length;

  const stockCount = history.filter((item) => item.asset_type === 'stock').length;
  const cryptoCount = history.filter((item) => item.asset_type === 'crypto').length;
  const newsCount = history.filter((item) => item.intent === 'GENERAL_FINANCIAL_NEWS').length;

  const buyCount = history.filter((item) => item.recommendation?.toUpperCase() === 'BUY').length;
  const holdCount = history.filter((item) => item.recommendation?.toUpperCase() === 'HOLD').length;
  const avoidCount = history.filter((item) => item.recommendation?.toUpperCase() === 'AVOID').length;

  const lowRiskCount = history.filter((item) => item.risk_level?.toLowerCase() === 'low').length;
  const medRiskCount = history.filter((item) => item.risk_level?.toLowerCase() === 'medium').length;
  const highRiskCount = history.filter((item) => item.risk_level?.toLowerCase() === 'high').length;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <PieChart size={24} color="#a855f7" />
            Financial Intelligence Analytics
          </h2>
          <p className="page-subtitle">
            Aggregation metrics computed from saved SQLite analysis logs and multi-agent query runs.
          </p>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Executed Analyses</div>
          <div className="metric-value">{totalAnalyses}</div>
          <div className="metric-sub">Recorded in SQLite History</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Stock vs Crypto Split</div>
          <div className="metric-value" style={{ fontSize: '1.4rem' }}>
            <span style={{ color: '#3b82f6' }}>{stockCount} Stock</span> / <span style={{ color: '#8b5cf6' }}>{cryptoCount} Crypto</span>
          </div>
          <div className="metric-sub">Equities vs Digital Assets</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Top Recommendation</div>
          <div className="metric-value" style={{ color: buyCount >= holdCount && buyCount >= avoidCount ? '#10b981' : '#f59e0b' }}>
            {totalAnalyses > 0 ? (buyCount >= holdCount ? 'BUY' : 'HOLD') : 'N/A'}
          </div>
          <div className="metric-sub">{buyCount} BUY • {holdCount} HOLD • {avoidCount} AVOID</div>
        </div>
      </div>

      {/* Breakdown Grids */}
      <div className="grid-2-col">
        {/* Asset Type Breakdown */}
        <div className="card">
          <div className="card-title">
            <Activity size={18} color="#a855f7" />
            Analysis Intent Distribution
          </div>
          <div className="analytics-bar-group">
            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span><TrendingUp size={14} color="#3b82f6" /> Stock Analyses</span>
                <strong>{stockCount} ({totalAnalyses > 0 ? Math.round((stockCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (stockCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#3b82f6' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span><Coins size={14} color="#8b5cf6" /> Crypto Analyses</span>
                <strong>{cryptoCount} ({totalAnalyses > 0 ? Math.round((cryptoCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (cryptoCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#8b5cf6' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span><Newspaper size={14} color="#10b981" /> Financial News Queries</span>
                <strong>{newsCount} ({totalAnalyses > 0 ? Math.round((newsCount / totalAnalyses) * 100) : 0}%)</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (newsCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#10b981' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Risk Level Distribution */}
        <div className="card">
          <div className="card-title">
            <ShieldAlert size={18} color="#f59e0b" />
            Risk Level Distribution
          </div>
          <div className="analytics-bar-group">
            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#10b981' }}>Low Risk</span>
                <strong>{lowRiskCount}</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (lowRiskCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#10b981' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#f59e0b' }}>Medium Risk</span>
                <strong>{medRiskCount}</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (medRiskCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#f59e0b' }} />
              </div>
            </div>

            <div className="analytics-bar-item">
              <div className="analytics-bar-label">
                <span style={{ color: '#ef4444' }}>High Risk</span>
                <strong>{highRiskCount}</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${totalAnalyses > 0 ? (highRiskCount / totalAnalyses) * 100 : 0}%`, backgroundColor: '#ef4444' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {totalAnalyses === 0 && (
        <div className="card empty-state-card">
          <PieChart size={44} color="#a855f7" style={{ opacity: 0.6 }} />
          <h3>No Analytics History Recorded Yet</h3>
          <p>
            Run financial queries to populate execution statistics and historical analytics graphs.
          </p>
        </div>
      )}
    </div>
  );
}
