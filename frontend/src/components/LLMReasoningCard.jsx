import React, { useState, useEffect } from 'react';
import { Sparkles, CheckCircle2, AlertTriangle, ShieldCheck, Cpu } from 'lucide-react';
import { authenticatedFetch } from '../services/apiClient';

export default function LLMReasoningCard({ analysisData }) {
  const [reasoning, setReasoning] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (analysisData && analysisData.success !== false) {
      fetchLLMReasoning();
    }
  }, [analysisData]);

  const fetchLLMReasoning = async () => {
    setLoading(true);
    try {
      const resp = await authenticatedFetch('/api/llm/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_data: analysisData,
          provider: 'auto',
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.success) {
          setReasoning(data);
        }
      }
    } catch (err) {
      console.warn('Could not fetch LLM reasoning synthesis:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!analysisData || analysisData.success === false) {
    return null;
  }

  return (
    <div className="card" style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)', border: '1px solid rgba(168, 85, 247, 0.4)', marginTop: '1.25rem' }}>
      <div className="card-title" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={20} color="#a855f7" />
          Autonomous LLM Financial Reasoning & Executive Summary
        </div>
        <span className="status-badge" style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', border: '1px solid rgba(168, 85, 247, 0.4)', fontSize: '0.75rem' }}>
          <Cpu size={12} /> {reasoning?.provider === 'offline_fallback' ? 'Hybrid Fallback Synthesizer' : `${reasoning?.provider?.toUpperCase()} AI`}
        </span>
      </div>

      {loading ? (
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0.75rem 0' }}>
          Synthesizing natural language executive reasoning...
        </div>
      ) : reasoning ? (
        <>
          {/* Executive Summary Narrative */}
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', padding: '1rem', borderRadius: '10px', marginBottom: '1rem', fontSize: '0.925rem', lineHeight: '1.6', color: '#f1f5f9' }}>
            {reasoning.executive_summary}
          </div>

          {/* Key Investment Takeaways */}
          {reasoning.key_takeaways && reasoning.key_takeaways.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                Key Agentic Insights & Takeaways
              </div>
              <ul className="factors-list">
                {reasoning.key_takeaways.map((item, idx) => (
                  <li key={idx} className="factor-item" style={{ fontSize: '0.875rem' }}>
                    <span className="factor-bullet" style={{ color: '#a855f7' }}>•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Risk Warning Box */}
          {reasoning.risk_warning && (
            <div className="info-box" style={{ borderColor: 'rgba(245, 158, 11, 0.4)', color: '#fbbf24', fontSize: '0.85rem' }}>
              <AlertTriangle size={16} />
              <span>{reasoning.risk_warning}</span>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
