import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AnalysisForm from './components/AnalysisForm';
import ResultCard from './components/ResultCard';
import HistoryList from './components/HistoryList';
import AgentDashboard from './components/AgentDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('main');
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState(null);

  // Fetch analysis history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const resp = await fetch('/api/history?limit=10');
      if (resp.ok) {
        const data = await resp.json();
        if (data.success && Array.isArray(data.analyses)) {
          setHistory(data.analyses);
        }
      }
    } catch (err) {
      console.warn('Could not fetch history log from server:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleStructuredAnalyze = async (payload) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSelectedId(null);

    try {
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await resp.json();
      if (!resp.ok) {
        setError(data.detail || data.error || 'Backend analysis request failed.');
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(`Backend Service Unavailable: Could not reach FastAPI server at http://127.0.0.1:8000. (${err.message})`);
    } finally {
      setLoading(false);
    }
  };

  const handleQueryAnalyze = async (payload) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSelectedId(null);

    try {
      const resp = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await resp.json();
      if (!resp.ok) {
        setError(data.detail || data.error || 'Query interpretation request failed.');
      } else {
        setResult(data);
        if (data.saved_analysis_id) {
          setSelectedId(data.saved_analysis_id);
          fetchHistory();
        }
      }
    } catch (err) {
      setError(`Backend Service Unavailable: Could not reach FastAPI server at http://127.0.0.1:8000. (${err.message})`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHistoryRecord = async (id) => {
    setLoading(true);
    setError(null);
    setSelectedId(id);

    try {
      const resp = await fetch(`/api/history/${id}`);
      if (resp.ok) {
        const data = await resp.json();
        if (data.success && data.analysis) {
          const record = data.analysis;
          setResult({
            success: true,
            saved_analysis_id: record.id,
            query: record.query,
            asset: record.asset,
            asset_type: record.asset_type,
            summary: `Historical Analysis Record #${record.id} for "${record.query}".`,
            disclaimer: 'Software-generated historical recommendation record retrieved from SQLite database.',
            recommendation: {
              recommendation: record.recommendation,
              confidence: record.confidence,
              recommendation_score: record.recommendation_score ?? null,
              factors: [
                `Historical market direction was ${record.market_direction || 'neutral'}.`,
                `Assessed risk level was ${record.risk_level || 'medium'} (Score: ${record.risk_score ?? '-'}).`,
                `Financial news sentiment was ${record.news_sentiment || 'neutral'}.`,
              ],
            },
            market_data: {
              symbol: record.asset,
              market_direction: record.market_direction,
            },
            risk_data: {
              risk_score: record.risk_score,
              risk_level: record.risk_level,
            },
            news_data: {
              overall_sentiment: record.news_sentiment,
            },
          });
        }
      } else {
        setError(`History record #${id} could not be found.`);
      }
    } catch (err) {
      setError(`Failed to retrieve history record #${id}: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const agentActivity = result?.agent_activity || result?.analysis?.agent_activity || [];

  return (
    <div className="container">
      <Header />

      {/* Navigation Tabs */}
      <div className="tabs" style={{ marginBottom: '1.75rem' }}>
        <button
          className={`tab-btn ${activeTab === 'main' ? 'active' : ''}`}
          onClick={() => setActiveTab('main')}
        >
          Financial Intelligence Dashboard
        </button>
        <button
          className={`tab-btn ${activeTab === 'agent' ? 'active' : ''}`}
          onClick={() => setActiveTab('agent')}
        >
          Agent Activity Dashboard {agentActivity.length > 0 ? `(${agentActivity.length})` : ''}
        </button>
      </div>

      {error && (
        <div className="error-box">
          <div>
            <strong>Service Notice:</strong> {error}
          </div>
        </div>
      )}

      {loading && (
        <div className="card loading-box">
          <div className="spinner"></div>
          <div>
            <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>
              Executing Autonomous Agent Intelligence Pipeline...
            </strong>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Sequential execution: Market Data Agent &rarr; News Agent &rarr; Risk Agent &rarr; Portfolio Agent
            </p>
          </div>
        </div>
      )}

      {/* Main Financial Dashboard Tab */}
      {activeTab === 'main' && (
        <>
          <AnalysisForm
            onAnalyze={handleStructuredAnalyze}
            onQuery={handleQueryAnalyze}
            loading={loading}
          />

          {result && !loading && <ResultCard result={result} />}

          <HistoryList
            history={history}
            selectedId={selectedId}
            onSelectRecord={handleSelectHistoryRecord}
            onRefresh={fetchHistory}
            loading={historyLoading}
          />
        </>
      )}

      {/* Agent Activity Dashboard Tab */}
      {activeTab === 'agent' && (
        <AgentDashboard agentActivity={agentActivity} />
      )}
    </div>
  );
}