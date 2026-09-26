import React from 'react';
import {
  TrendingUp,
  Coins,
  Newspaper,
  ShieldAlert,
  Briefcase,
  Bot,
  Cpu,
  ArrowRight,
  GitBranch,
  Info,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  Compass
} from 'lucide-react';

const AGENT_NAMES = {
  Orchestrator: 'System Orchestrator',
  StockAgent: 'Stock Price Agent',
  CryptoAgent: 'Crypto Market Agent',
  NewsAgent: 'Financial News Agent',
  RiskAgent: 'Volatility Risk Agent',
  PortfolioAgent: 'Portfolio Advisor Agent'
};

export default function DecisionTrace({ trace = [] }) {
  if (!trace || !Array.isArray(trace) || trace.length === 0) {
    return (
      <div className="card" style={{ padding: '1.25rem', borderRadius: '10px', marginTop: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          <Info size={18} color="var(--accent-blue)" />
          <span>Decision trace is not available for this analysis.</span>
        </div>
      </div>
    );
  }

  const getAgentIcon = (agent) => {
    switch (agent) {
      case 'Orchestrator':
        return <Cpu size={18} color="var(--accent-blue)" />;
      case 'StockAgent':
        return <TrendingUp size={18} color="#60a5fa" />;
      case 'CryptoAgent':
        return <Coins size={18} color="#f59e0b" />;
      case 'NewsAgent':
        return <Newspaper size={18} color="#a855f7" />;
      case 'RiskAgent':
        return <ShieldAlert size={18} color="#ef4444" />;
      case 'PortfolioAgent':
        return <Briefcase size={18} color="#10b981" />;
      default:
        return <Bot size={18} color="var(--text-muted)" />;
    }
  };

  const getResultBadgeClass = (res) => {
    if (!res) return 'badge-conf';
    const val = String(res).toLowerCase();
    if (['buy', 'bullish', 'positive', 'low'].includes(val)) {
      return 'badge-buy';
    }
    if (['avoid', 'bearish', 'high', 'failed', 'blocked', 'unsupported'].includes(val)) {
      return 'badge-avoid';
    }
    return 'badge-hold';
  };

  return (
    <div className="card" style={{ marginTop: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Compass size={22} color="var(--accent-purple)" />
          <h3 className="card-title" style={{ margin: 0, fontSize: '1.15rem' }}>
            Agentic Decision Trace & Explainability
          </h3>
        </div>
        <span className="badge badge-conf" style={{ fontSize: '0.8rem' }}>
          {trace.length} {trace.length === 1 ? 'Step' : 'Steps'} Evaluated
        </span>
      </div>

      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
        Step-by-step reasoning log showing intent classification, target agent routing, intermediate decisions, and recommendation rationale.
      </p>

      {/* Sequential Decision Trace Timeline */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {trace.map((item, idx) => {
          const stepNum = item.step || idx + 1;
          const agentName = item.agent || 'UnknownAgent';
          const action = item.action || 'evaluate';
          const reason = item.reason || null;
          const resultVal = item.result || 'N/A';
          const nextDecision = item.next_decision || null;

          const isLast = idx === trace.length - 1;
          const isHalt = String(resultVal).toLowerCase() === 'unsupported' || String(nextDecision).toLowerCase().includes('halt') || String(resultVal).toLowerCase() === 'failed';

          return (
            <div
              key={idx}
              style={{
                background: 'rgba(11, 15, 25, 0.65)',
                border: `1px solid ${isHalt ? 'rgba(239, 68, 68, 0.4)' : 'var(--border-color)'}`,
                borderRadius: '10px',
                padding: '1.1rem',
                position: 'relative'
              }}
            >
              {/* Header Line of Step Card */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.6rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
                  <span className="badge badge-conf" style={{ fontWeight: 800 }}>
                    Step #{stepNum}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {getAgentIcon(agentName)}
                    <span>{AGENT_NAMES[agentName] || agentName}</span>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(255, 255, 255, 0.05)', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                    {action}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Result:</span>
                  <span className={`badge ${getResultBadgeClass(resultVal)}`} style={{ fontSize: '0.8rem', padding: '0.2rem 0.65rem' }}>
                    {String(resultVal).toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Reason Body */}
              {reason && (
                <div style={{ fontSize: '0.875rem', color: 'var(--text-main)', marginBottom: '0.6rem', lineHeight: '1.4' }}>
                  <strong style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Rationale:{' '}
                  </strong>
                  <span>{reason}</span>
                </div>
              )}

              {/* Next Decision Banner */}
              {nextDecision && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', color: 'var(--accent-blue)', background: 'rgba(59, 130, 246, 0.08)', padding: '0.45rem 0.75rem', borderRadius: '6px', borderLeft: `3px solid ${isHalt ? 'var(--red-avoid)' : 'var(--accent-blue)'}` }}>
                  <ArrowRight size={14} style={{ flexShrink: 0 }} />
                  <div>
                    <strong>Next Action:</strong> {nextDecision}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
