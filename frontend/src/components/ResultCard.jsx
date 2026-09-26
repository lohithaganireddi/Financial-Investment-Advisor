import React from 'react';
import { Award, ShieldAlert, Newspaper, TrendingUp, Info, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import DecisionTrace from './DecisionTrace';
import LLMReasoningCard from './LLMReasoningCard';

export default function ResultCard({ result }) {
  if (!result) return null;

  // Unpack structured or query response
  const isQueryResponse = 'interpreted' in result;
  const analysisData = isQueryResponse ? result.analysis : result;
  const queryPrompt = isQueryResponse ? result.query : null;
  const decisionTrace = result.decision_trace || analysisData?.decision_trace || result?.analysis?.decision_trace || [];

  if (!analysisData || analysisData.success === false) {
    return (
      <div className="error-box" style={{ display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.68rem' }}>
          <AlertTriangle size={20} style={{ flexShrink: 0 }} />
          <div>
            <strong>Analysis Pipeline Warning:</strong> {analysisData?.error || result?.error || 'Unable to complete financial analysis.'}
          </div>
        </div>
        {decisionTrace && decisionTrace.length > 0 && (
          <DecisionTrace trace={decisionTrace} />
        )}
      </div>
    );
  }

  const hasRecommendation = Boolean(
    analysisData.recommendation &&
    analysisData.recommendation.success !== false &&
    analysisData.recommendation.recommendation
  );

  const recommendationData = hasRecommendation ? analysisData.recommendation : {};
  const marketData = analysisData.market_data || {};
  const riskData = analysisData.risk_data || {};
  const newsData = analysisData.news_data || {};

  const rec = hasRecommendation ? String(recommendationData.recommendation).toLowerCase() : 'unavailable';
  const confidence = hasRecommendation ? String(recommendationData.confidence || 'medium').toLowerCase() : 'n/a';
  const score = hasRecommendation ? recommendationData.recommendation_score ?? null : null;

  const assetName = analysisData.asset || marketData.symbol || marketData.coin_id || 'Asset';
  const assetType = (analysisData.asset_type || 'asset').toUpperCase();

  const price = marketData.price;
  const changePct = marketData.change_percent ?? marketData.change_percent_24h;

  const recBadgeClass = !hasRecommendation
    ? 'badge-conf'
    : rec === 'buy'
    ? 'badge-buy'
    : rec === 'avoid'
    ? 'badge-avoid'
    : 'badge-hold';

  const recColor = !hasRecommendation
    ? 'var(--text-muted)'
    : rec === 'buy'
    ? 'var(--green-buy)'
    : rec === 'avoid'
    ? 'var(--red-avoid)'
    : 'var(--amber-hold)';

  const riskScore = riskData.risk_score ?? 50;
  const riskLevel = (riskData.risk_level || 'medium').toLowerCase();
  const riskColor = riskLevel === 'high' ? 'var(--red-avoid)' : riskLevel === 'low' ? 'var(--green-buy)' : 'var(--amber-hold)';

  const agentActivity = result.agent_activity || analysisData.agent_activity || [];

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>{assetName.toUpperCase()}</h2>
            <span className="badge badge-conf">{assetType}</span>
            {'saved_analysis_id' in result && result.saved_analysis_id && (
              <span className="badge badge-conf">Saved ID #{result.saved_analysis_id}</span>
            )}
          </div>
          {queryPrompt && (
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Query Prompt: "{queryPrompt}"
            </div>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <span className={`badge ${recBadgeClass}`} style={{ fontSize: '1rem', padding: '0.55rem 1.25rem' }}>
            RECOMMENDATION: {hasRecommendation ? rec.toUpperCase() : 'UNAVAILABLE'}
          </span>
          {hasRecommendation && (
            <span className="badge badge-conf">Confidence: {confidence.toUpperCase()}</span>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        {/* Rec Score */}
        <div className="metric-card">
          <div className="metric-label">Rec Score</div>
          <div className="metric-value" style={{ color: recColor }}>
            {typeof score === 'number' ? `${score} / 100` : 'N/A'}
          </div>
          {typeof score === 'number' && (
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: `${Math.min(100, Math.max(0, score))}%`, backgroundColor: recColor }}></div>
            </div>
          )}
        </div>

        {/* Current Price */}
        {price !== undefined && (
          <div className="metric-card">
            <div className="metric-label">Current Price</div>
            <div className="metric-value">
              ${typeof price === 'number' ? price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : price}
            </div>
          </div>
        )}

        {/* 24h / Session Change */}
        {changePct !== undefined && (
          <div className="metric-card">
            <div className="metric-label">Session / 24h Change</div>
            <div className="metric-value" style={{ color: changePct > 0 ? 'var(--green-buy)' : changePct < 0 ? 'var(--red-avoid)' : 'var(--text-main)' }}>
              {changePct > 0 ? '+' : ''}{typeof changePct === 'number' ? changePct.toFixed(2) : changePct}%
            </div>
          </div>
        )}

        {/* Market Direction */}
        <div className="metric-card">
          <div className="metric-label">Market Direction</div>
          <div className="metric-value" style={{ textTransform: 'capitalize' }}>
            {marketData.market_direction || 'Neutral'}
          </div>
        </div>

        {/* Risk Level */}
        <div className="metric-card">
          <div className="metric-label">Risk Level</div>
          <div className="metric-value" style={{ color: riskColor, textTransform: 'capitalize' }}>
            {riskLevel} ({riskScore})
          </div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${Math.min(100, Math.max(0, riskScore))}%`, backgroundColor: riskColor }}></div>
          </div>
        </div>

        {/* News Sentiment */}
        <div className="metric-card">
          <div className="metric-label">News Sentiment</div>
          <div className="metric-value" style={{ textTransform: 'capitalize' }}>
            {newsData.overall_sentiment || 'Neutral'}
          </div>
        </div>
      </div>

      {/* Agent Activity Section */}
      {agentActivity && agentActivity.length > 0 && (
        <div style={{ marginTop: '1.25rem' }}>
          <strong style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '0.5rem' }}>
            Agent Execution Activity
          </strong>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {agentActivity.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.5)', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                <span className="badge badge-conf" style={{ fontSize: '0.75rem' }}>#{item.order}</span>
                <strong style={{ color: 'var(--text-main)' }}>{item.agent}</strong>
                <span className={`badge ${item.status === 'success' ? 'badge-buy' : 'badge-avoid'}`} style={{ fontSize: '0.7rem', padding: '0.15rem 0.5rem' }}>
                  {item.status.toUpperCase()}
                </span>
                <span style={{ color: 'var(--text-muted)', flex: 1 }}>{item.summary}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decision Trace & Explainability Section */}
      <DecisionTrace trace={decisionTrace} />

      {/* Autonomous LLM Reasoning Synthesis */}
      <LLMReasoningCard analysisData={analysisData} />

      {/* Summary */}
      <div style={{ background: 'rgba(11, 15, 25, 0.6)', padding: '1.1rem', borderRadius: '10px', borderLeft: `4px solid ${hasRecommendation ? 'var(--accent-blue)' : 'var(--amber-hold)'}`, margin: '1.25rem 0' }}>
        <strong style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Executive Agent Summary
        </strong>
        <p style={{ fontSize: '0.95rem', lineHeight: '1.5' }}>
          {analysisData.summary || (!hasRecommendation ? 'Portfolio recommendation is unavailable because required prerequisite context (such as news or risk evaluation) was missing or failed. Market and risk metrics evaluated prior to pipeline block are preserved below.' : 'No summary provided.')}
        </p>
      </div>

      {/* Key Factors */}
      {recommendationData.factors && recommendationData.factors.length > 0 && (
        <div style={{ marginTop: '1.25rem' }}>
          <strong style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Decision Rationale Factors
          </strong>
          <ul className="factors-list">
            {recommendationData.factors.map((factor, idx) => (
              <li key={idx}>
                <CheckCircle2 size={16} color="#3b82f6" style={{ flexShrink: 0 }} />
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Educational Disclaimer */}
      <div className="disclaimer-box">
        <Info size={16} style={{ flexShrink: 0, color: 'var(--text-muted)' }} />
        <div>
          <strong>Educational & Portfolio Disclaimer:</strong>{' '}
          {analysisData.disclaimer || recommendationData.disclaimer || 'This is a software-generated educational recommendation produced by autonomous AI agents, not certified financial advice.'}
        </div>
      </div>
    </div>
  );
}