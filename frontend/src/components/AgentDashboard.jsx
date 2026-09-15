import React from 'react';
import {
  TrendingUp,
  Coins,
  Newspaper,
  ShieldAlert,
  Briefcase,
  Bot,
  CheckCircle2,
  XCircle,
  Activity,
  Layers,
  Cpu,
  ArrowRight,
  Search,
  Award
} from 'lucide-react';

const FRIENDLY_NAMES = {
  StockAgent: 'Stock Price Agent',
  CryptoAgent: 'Crypto Agent',
  NewsAgent: 'Financial News Agent',
  RiskAgent: 'Risk Analysis Agent',
  PortfolioAgent: 'Portfolio Recommendation Agent'
};

export default function AgentDashboard({ agentActivity = [], context = null }) {
  const totalAgents = agentActivity.length;
  const successfulAgents = agentActivity.filter(a => a.status === 'success').length;
  const failedAgents = agentActivity.filter(a => a.status !== 'success').length;

  let pipelineStatus = 'NO ACTIVITY';
  let statusColor = 'var(--text-muted)';
  if (totalAgents > 0) {
    if (failedAgents === 0) {
      pipelineStatus = 'COMPLETED';
      statusColor = 'var(--green-buy)';
    } else if (successfulAgents > 0) {
      pipelineStatus = 'PARTIAL FAILURE';
      statusColor = 'var(--amber-hold)';
    } else {
      pipelineStatus = 'FAILED';
      statusColor = 'var(--red-avoid)';
    }
  }

  const getAgentIcon = (name) => {
    switch (name) {
      case 'StockAgent':
        return <TrendingUp size={20} color="#60a5fa" />;
      case 'CryptoAgent':
        return <Coins size={20} color="#f59e0b" />;
      case 'NewsAgent':
        return <Newspaper size={20} color="#a855f7" />;
      case 'RiskAgent':
        return <ShieldAlert size={20} color="#ef4444" />;
      case 'PortfolioAgent':
        return <Briefcase size={20} color="#10b981" />;
      default:
        return <Bot size={20} color="#3b82f6" />;
    }
  };

  const getFriendlyName = (name) => FRIENDLY_NAMES[name] || name;

  if (!agentActivity || agentActivity.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
        <div style={{ display: 'inline-flex', padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '50%', marginBottom: '1.25rem' }}>
          <Cpu size={40} color="var(--accent-blue)" />
        </div>
        <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          No Agent Activity Available
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '500px', margin: '0 auto 1.5rem' }}>
          Run a financial analysis or query to view the autonomous multi-agent execution pipeline in real-time.
        </p>
      </div>
    );
  }

  // Derive context titles
  const assetLabel = context?.asset ? context.asset.toUpperCase() : null;
  const assetType = context?.asset_type ? context.asset_type.toUpperCase() : null;
  const intent = context?.intent || null;
  const queryText = context?.query || null;
  const rec = context?.recommendation ? context.recommendation.toUpperCase() : null;
  const riskLevel = context?.risk_level ? context.risk_level.toUpperCase() : null;

  let subtitleText = 'Execution pipeline telemetry log';
  if (assetLabel && assetType) {
    subtitleText = `Execution pipeline for ${assetLabel} (${assetType}) analysis`;
  } else if (intent === 'GENERAL_FINANCIAL_NEWS') {
    subtitleText = 'Execution pipeline for General Financial News Analysis';
  } else if (queryText) {
    subtitleText = `Execution pipeline for query: "${queryText}"`;
  }

  return (
    <div className="agent-dashboard-container">
      {/* Top Header Summary with Analysis Context */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 className="card-title" style={{ fontSize: '1.4rem', margin: 0 }}>
              <Activity size={24} color="var(--accent-blue)" />
              Agent Execution Activity
            </h2>
            <p style={{ fontSize: '0.9rem', color: 'var(--accent-blue)', fontWeight: 600, marginTop: '0.3rem' }}>
              {subtitleText}
            </p>
            {queryText && (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Query Prompt: "{queryText}"
              </p>
            )}
          </div>

          {/* Context Badges */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            {assetLabel && <span className="badge badge-conf">{assetLabel}</span>}
            {assetType && <span className="badge badge-conf">{assetType}</span>}
            {rec && (
              <span className={`badge ${rec === 'BUY' ? 'badge-buy' : rec === 'AVOID' ? 'badge-avoid' : 'badge-hold'}`}>
                REC: {rec}
              </span>
            )}
            {riskLevel && <span className="badge badge-conf">RISK: {riskLevel}</span>}
            {context?.saved_id && <span className="badge badge-conf">Saved ID #{context.saved_id}</span>}
          </div>
        </div>

        {/* Dynamic Horizontal Pipeline Summary Flow */}
        <div style={{ marginTop: '1.25rem', paddingTop: '1.1rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <strong style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '0.75rem' }}>
            Executed Pipeline Flow
          </strong>
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            {agentActivity.map((item, idx) => (
              <React.Fragment key={idx}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(11, 15, 25, 0.7)', padding: '0.45rem 0.8rem', borderRadius: '8px', border: `1px solid ${item.status === 'success' ? 'var(--border-color)' : 'rgba(239, 68, 68, 0.4)'}` }}>
                  {getAgentIcon(item.agent)}
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {getFriendlyName(item.agent)}
                  </span>
                </div>
                {idx < agentActivity.length - 1 && (
                  <ArrowRight size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Cards Grid */}
      <div className="metrics-grid" style={{ marginBottom: '1.75rem' }}>
        <div className="metric-card">
          <div className="metric-label">Total Executed</div>
          <div className="metric-value">{totalAgents}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Successful</div>
          <div className="metric-value" style={{ color: 'var(--green-buy)' }}>{successfulAgents}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Failed</div>
          <div className="metric-value" style={{ color: failedAgents > 0 ? 'var(--red-avoid)' : 'var(--text-muted)' }}>
            {failedAgents}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Pipeline Status</div>
          <div className="metric-value" style={{ color: statusColor, fontSize: '1.1rem' }}>
            {pipelineStatus}
          </div>
        </div>
      </div>

      {/* Vertical Execution Timeline */}
      <div className="card">
        <h3 className="card-title" style={{ fontSize: '1.15rem', marginBottom: '1.5rem' }}>
          <Layers size={20} color="var(--accent-purple)" />
          Sequential Execution Timeline
        </h3>

        <div style={{ position: 'relative', paddingLeft: '2.5rem', margin: '0.5rem 0 1.5rem' }}>
          {/* Vertical Connecting Line */}
          <div
            style={{
              position: 'absolute',
              left: '1.1rem',
              top: '1rem',
              bottom: '1rem',
              width: '2px',
              background: 'linear-gradient(to bottom, var(--accent-blue), var(--accent-purple))',
              zIndex: 0
            }}
          />

          {agentActivity.map((item, index) => {
            const isSuccess = item.status === 'success';

            return (
              <div
                key={index}
                style={{
                  position: 'relative',
                  marginBottom: index === agentActivity.length - 1 ? 0 : '1.75rem',
                  zIndex: 1
                }}
              >
                {/* Step Node Marker Icon */}
                <div
                  style={{
                    position: 'absolute',
                    left: '-2.5rem',
                    top: '0.2rem',
                    width: '2.2rem',
                    height: '2.2rem',
                    borderRadius: '50%',
                    background: '#0b0f19',
                    border: `2px solid ${isSuccess ? 'var(--green-buy)' : 'var(--red-avoid)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: `0 0 10px ${isSuccess ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
                  }}
                >
                  {isSuccess ? (
                    <CheckCircle2 size={16} color="var(--green-buy)" />
                  ) : (
                    <XCircle size={16} color="var(--red-avoid)" />
                  )}
                </div>

                {/* Timeline Card */}
                <div
                  style={{
                    background: 'rgba(11, 15, 25, 0.7)',
                    border: `1px solid ${isSuccess ? 'var(--border-color)' : 'rgba(239, 68, 68, 0.4)'}`,
                    borderRadius: '10px',
                    padding: '1.1rem',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      {getAgentIcon(item.agent)}
                      <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {getFriendlyName(item.agent)}
                      </span>
                      <span className="badge badge-conf" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        {item.agent}
                      </span>
                      <span className="badge badge-conf" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        #{item.order}
                      </span>
                    </div>

                    <span className={`badge ${isSuccess ? 'badge-buy' : 'badge-avoid'}`}>
                      {item.status.toUpperCase()}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                    {item.summary}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Agent Details Section */}
      <div className="card">
        <h3 className="card-title" style={{ fontSize: '1.15rem', marginBottom: '1.25rem' }}>
          Agent Execution Telemetry & Details
        </h3>

        <div className="table-container">
          <table className="history-table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Friendly Name</th>
                <th>System Agent ID</th>
                <th>Status</th>
                <th>Execution Summary</th>
              </tr>
            </thead>
            <tbody>
              {agentActivity.map((item, idx) => (
                <tr key={idx}>
                  <td>
                    <span className="badge badge-conf">#{item.order}</span>
                  </td>
                  <td style={{ fontWeight: 700 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {getAgentIcon(item.agent)}
                      {getFriendlyName(item.agent)}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-conf">{item.agent}</span>
                  </td>
                  <td>
                    <span className={`badge ${item.status === 'success' ? 'badge-buy' : 'badge-avoid'}`}>
                      {item.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{item.summary}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
