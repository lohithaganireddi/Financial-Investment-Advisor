import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, AlertTriangle, CheckCircle, Flame, ArrowUpRight, ArrowDownRight, Minus, TrendingUp, Coins } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';

export default function RiskDashboard() {
  const { result, analysisContext } = useFinancial();

  const riskData = result?.risk_data;
  const marketData = result?.market_data;
  const riskLevel = riskData?.risk_level || analysisContext?.risk_level || 'Unknown';
  const riskScore = riskData?.risk_score ?? '-';
  const marketDirection = marketData?.market_direction || 'neutral';
  const asset = analysisContext?.asset || result?.asset || 'Selected Asset';

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#94a3b8';
    }
  };

  const riskColor = getRiskColor(riskLevel);

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <ShieldAlert size={24} color="#f59e0b" />
            Volatility & Risk Dashboard
          </h2>
          <p className="page-subtitle">
            Comprehensive market volatility risk assessment, score metrics, and risk factors.
          </p>
        </div>
      </div>

      {riskData ? (
        <>
          {/* Top Metric Cards Grid */}
          <div className="metrics-grid">
            <div className="metric-card" style={{ borderLeft: `4px solid ${riskColor}` }}>
              <div className="metric-label">Assessed Risk Level</div>
              <div className="metric-value" style={{ color: riskColor }}>
                {riskLevel.toUpperCase()}
              </div>
              <div className="metric-sub">Asset: {asset}</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Volatility Risk Score</div>
              <div className="metric-value">{riskScore} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ 100</span></div>
              <div className="metric-sub">Calculated by RiskAgent</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Market Direction</div>
              <div className="metric-value" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {marketDirection === 'bullish' && <ArrowUpRight color="#10b981" size={24} />}
                {marketDirection === 'bearish' && <ArrowDownRight color="#ef4444" size={24} />}
                {marketDirection === 'neutral' && <Minus color="#f59e0b" size={24} />}
                {marketDirection.toUpperCase()}
              </div>
              <div className="metric-sub">Short-term trend direction</div>
            </div>
          </div>

          {/* Risk Factors Breakdown */}
          <div className="card">
            <div className="card-title">
              <AlertTriangle size={18} color={riskColor} />
              Risk Rationale & Exposure Factors
            </div>
            
            <div className="info-box" style={{ marginBottom: '1.25rem', borderColor: `${riskColor}40` }}>
              Analysis Record for <strong>{asset}</strong> ({analysisContext?.asset_type?.toUpperCase() || 'EQUITY/CRYPTO'}). Saved ID: #{analysisContext?.saved_id || 'Active'}.
            </div>

            <div className="risk-factors-list">
              <div className="risk-factor-item">
                <Flame size={18} color={riskColor} />
                <div>
                  <strong>Price Volatility Exposure:</strong> Market direction for {asset} is assessed as <em>{marketDirection}</em> with a numeric risk score of {riskScore}.
                </div>
              </div>
              <div className="risk-factor-item">
                <CheckCircle size={18} color="#10b981" />
                <div>
                  <strong>Agent Risk Rating:</strong> RiskAgent assigned a <strong>{riskLevel.toUpperCase()}</strong> risk classification.
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="card empty-state-card">
          <ShieldAlert size={44} color="#f59e0b" style={{ opacity: 0.6 }} />
          <h3>No Analysis Available Yet</h3>
          <p>
            Run an analysis from the Stock or Crypto page to generate a real-time risk assessment score.
          </p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <Link to="/stocks" className="btn-primary" style={{ textDecoration: 'none', width: 'auto' }}>
              <TrendingUp size={16} /> Go to Stock Analysis
            </Link>
            <Link to="/crypto" className="btn-primary" style={{ textDecoration: 'none', width: 'auto', backgroundColor: '#8b5cf6' }}>
              <Coins size={16} /> Go to Crypto Analysis
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
