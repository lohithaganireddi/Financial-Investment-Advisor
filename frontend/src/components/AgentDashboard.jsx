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
  Cpu
} from 'lucide-react';

export default function AgentDashboard({ agentActivity = [] }) {
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

  return (
    <div className="agent-dashboard-container">
      {/* Top Header Summary */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 className="card-title" style={{ fontSize: '1.4rem', margin: 0 }}>
            <Activity size={24} color="var(--accent-blue)" />
            Agent Execution Activity Dashboard
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Real-time execution sequence and agent telemetry
          </p>
        </div>
      </div>

      {/* Summary Cards Grid */}
      <div className="metrics-grid" style={{ marginBottom: '2rem' }}>
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
                <th>Agent Name</th>
                <th>Execution Status</th>
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
                      {item.agent}
                    </div>
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
