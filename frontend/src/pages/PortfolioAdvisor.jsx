import React from 'react';
import { Briefcase, CheckCircle2, AlertCircle, TrendingUp, ShieldAlert, Newspaper, Info } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';

export default function PortfolioAdvisor() {
  const { result, analysisContext } = useFinancial();

  const recData = result?.recommendation || result?.analysis?.recommendation;
  const recommendation = recData?.recommendation || analysisContext?.recommendation || 'UNKNOWN';
  const confidence = recData?.confidence || 'medium';
  const recScore = recData?.recommendation_score ?? '-';
  const factors = recData?.factors || [];
  const disclaimer = result?.disclaimer || 'Software-generated financial recommendation for informational purposes.';

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
            Synthesized multi-agent intelligence providing actionable investment guidance.
          </p>
        </div>
      </div>

      {recData ? (
        <>
          {/* Main Recommendation Hero Banner */}
          <div className="card recommendation-hero-card">
            <div className="hero-rec-header">
              <div>
                <span className="hero-rec-label">Asset: {analysisContext?.asset || result?.asset || 'Target Asset'}</span>
                <div className={`recommendation-badge ${getRecClass(recommendation)}`} style={{ fontSize: '1.5rem', padding: '0.6rem 1.5rem', marginTop: 8 }}>
                  {recommendation.toUpperCase()}
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
        <div className="card empty-state-card">
          <Briefcase size={44} color="#ec4899" style={{ opacity: 0.6 }} />
          <h3>No Portfolio Recommendation Active</h3>
          <p>
            Execute an analysis from the AI Dashboard, Stock, or Crypto page to generate an autonomous portfolio recommendation.
          </p>
        </div>
      )}
    </div>
  );
}
