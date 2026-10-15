import React, { useState, useEffect } from 'react';
import { Bot, Activity, Cpu, Gauge, Clock, ShieldCheck, RefreshCw, BarChart2 } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import AgentDashboard from '../components/AgentDashboard';

import { authenticatedFetch } from '../services/apiClient';

export default function AgentActivity() {
  const { agentActivity, decisionTrace, analysisContext } = useFinancial();
  const [telemetry, setTelemetry] = useState(null);
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);

  const fetchTelemetry = async () => {
    setLoadingTelemetry(true);
    try {
      const res = await authenticatedFetch('/api/telemetry/metrics');
      if (res.ok) {
        const data = await res.json();
        setTelemetry(data);
      }
    } catch (err) {
      console.error('Failed to fetch system telemetry:', err);
    } finally {
      setLoadingTelemetry(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, []);

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="page-title">
            <Bot size={24} color="#06b6d4" />
            Agent Activity & Execution Telemetry
          </h2>
          <p className="page-subtitle">
            Real-time tracking of multi-agent pipeline order, step-by-step execution summaries, decision traces, and system latency metrics.
          </p>
        </div>
        <button
          onClick={fetchTelemetry}
          className="tab-btn"
          disabled={loadingTelemetry}
          style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
        >
          <RefreshCw size={14} className={loadingTelemetry ? 'spinner' : ''} />
          {loadingTelemetry ? 'Refreshing...' : 'Refresh Metrics'}
        </button>
      </div>

      {/* System Telemetry Metrics Overview Card */}
      {telemetry && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div className="card-title" style={{ justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Gauge size={20} color="#06b6d4" />
              <span>System-Wide Multi-Agent Performance Telemetry</span>
            </div>
            <span className={`badge ${telemetry.health_status === 'healthy' ? 'badge-buy' : 'badge-avoid'}`}>
              HEALTH: {telemetry.health_status?.toUpperCase()}
            </span>
          </div>

          <div className="metrics-grid" style={{ marginTop: '1rem' }}>
            <div className="metric-card">
              <div className="metric-label">Avg Pipeline Latency</div>
              <div className="metric-value" style={{ color: '#60a5fa' }}>
                {telemetry.average_latency_ms} <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>ms</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Total Pipeline Requests</div>
              <div className="metric-value" style={{ color: '#a855f7' }}>
                {telemetry.total_requests}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Success Rate</div>
              <div className="metric-value" style={{ color: 'var(--green-buy)' }}>
                {telemetry.success_rate_percent}%
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Failed Requests</div>
              <div className="metric-value" style={{ color: telemetry.failed_requests > 0 ? 'var(--red-avoid)' : 'var(--text-muted)' }}>
                {telemetry.failed_requests}
              </div>
            </div>
          </div>

          {/* Per-Agent Metrics Table */}
          {telemetry.per_agent_metrics && (
            <div style={{ marginTop: '1.5rem', paddingTop: '1.2rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
              <strong style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '0.75rem' }}>
                Per-Agent Telemetry Statistics
              </strong>
              <div className="table-container">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Agent Module</th>
                      <th>Total Calls</th>
                      <th>Successes</th>
                      <th>Failures</th>
                      <th>Avg Exec Time</th>
                      <th>Success Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(telemetry.per_agent_metrics).map(([agentName, stats]) => (
                      <tr key={agentName}>
                        <td style={{ fontWeight: 700 }}>{agentName}</td>
                        <td>{stats.calls}</td>
                        <td style={{ color: 'var(--green-buy)', fontWeight: 600 }}>{stats.successes}</td>
                        <td style={{ color: stats.failures > 0 ? 'var(--red-avoid)' : 'var(--text-muted)' }}>{stats.failures}</td>
                        <td>{stats.avg_time_ms} ms</td>
                        <td>
                          <span className={`badge ${stats.success_rate >= 90 ? 'badge-buy' : stats.success_rate >= 70 ? 'badge-hold' : 'badge-avoid'}`}>
                            {stats.success_rate}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      <AgentDashboard agentActivity={agentActivity} context={analysisContext} decisionTrace={decisionTrace} />
    </div>
  );
}
