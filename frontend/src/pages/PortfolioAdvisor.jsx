import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, CheckCircle2, Info, TrendingUp, Coins, FileText } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import BacktestVisualizer from '../components/BacktestVisualizer';
import WatchlistWidget from '../components/WatchlistWidget';
import ExportReportModal from '../components/ExportReportModal';

export default function PortfolioAdvisor() {
  const { result, analysisContext } = useFinancial();
  const [exportModalOpen, setExportModalOpen] = useState(false);

  const recData = result?.recommendation;
  const recommendation = recData?.recommendation || analysisContext?.recommendation || 'UNKNOWN';
  const confidence = recData?.confidence || 'medium';
  const recScore = recData?.recommendation_score ?? '-';
  const factors = recData?.factors || [];
  const disclaimer = result?.disclaimer || 'Software-generated financial recommendation for informational purposes.';

  const activeAsset = analysisContext?.asset || result?.asset || 'AAPL';
  const activeAssetType = analysisContext?.asset_type || result?.asset_type || 'stock';
  const activeRiskScore = result?.risk_data?.risk_score ?? analysisContext?.risk_score ?? null;

  const getRecClass = (rec) => {
    switch (rec?.toUpperCase()) {
      case 'BUY': return 'rec-buy';
      case 'HOLD': return 'rec-hold';
      case 'AVOID': return 'rec-avoid';
      default: return '';
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <Briefcase size={24} color="#ec4899" />
            Portfolio Recommendation Advisor
          </h2>
          <p className="page-subtitle">
            Synthesized multi-agent intelligence providing autonomous investment guidance & backtesting.
          </p>
        </div>
      </div>

      {/* Personalized User Watchlist Live Monitoring */}
      <WatchlistWidget />

      {recData ? (
        <>
          {/* Main Recommendation Hero Banner */}
          <div className="card recommendation-hero-card">
            <div className="hero-rec-header">
              <div>
                <span className="hero-rec-label">Asset: {activeAsset}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: 8, flexWrap: 'wrap' }}>
                  <div className={`recommendation-badge ${getRecClass(recommendation)}`} style={{ fontSize: '1.5rem', padding: '0.6rem 1.5rem' }}>
                    {recommendation.toUpperCase()}
                  </div>
                  <button
                    onClick={() => setExportModalOpen(true)}
                    className="tab-btn"
                    style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.4rem', backgroundColor: 'rgba(59, 130, 246, 0.15)', borderColor: 'rgba(59, 130, 246, 0.4)', color: '#60a5fa', fontWeight: 600 }}
                  >
                    <FileText size={15} /> Export Report
                  </button>
                </div>
              </div>

              <div className="hero-rec-metrics">
                <div className="hero-metric-box">
                  <div className="hero-metric-label">Recommendation Score</div>
                  <div className="hero-metric-val">{recScore} <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>/ 100</span></div>
                </div>
                <div className="hero-metric-box">
                  <div className="hero-metric-label">Agent Confidence</div>
                  <div className="hero-metric-val">{confidence.toUpperCase()}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Rationale Factors */}
          <div className="card">
            <div className="card-title">
              <CheckCircle2 size={18} color="#ec4899" />
              Supporting Rationale & Agent Synthesis
            </div>

            {factors.length > 0 ? (
              <ul className="factors-list">
                {factors.map((factor, idx) => (
                  <li key={idx} className="factor-item">
                    <span className="factor-bullet">•</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>
                Synthesized from Market Data Agent, News Agent, and Risk Agent.
              </p>
            )}

            <div className="disclaimer-box" style={{ marginTop: '1.5rem' }}>
              <Info size={16} />
              <span>{disclaimer}</span>
            </div>
          </div>
        </>
      ) : (
        <div className="card empty-state-card" style={{ marginBottom: '1.75rem' }}>
          <Briefcase size={44} color="#ec4899" style={{ opacity: 0.6 }} />
          <h3>No Portfolio Recommendation Active</h3>
          <p>
            Execute an analysis from the Stock or Crypto page or select an asset from your Watchlist above.
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

      {/* Interactive Backtesting Engine Visualizer */}
      <BacktestVisualizer
        initialAsset={activeAsset}
        initialAssetType={activeAssetType}
        riskScore={activeRiskScore}
      />

      <ExportReportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        analysis={{
          id: result?.saved_analysis_id || result?.id || analysisContext?.saved_analysis_id,
          asset: activeAsset,
          asset_type: activeAssetType,
          recommendation: recommendation,
          recommendation_score: recScore,
          confidence: confidence,
          risk_score: activeRiskScore,
          factors: factors,
          agent_activity: result?.agent_activity || [],
          ...result
        }}
      />
    </div>
  );
}
