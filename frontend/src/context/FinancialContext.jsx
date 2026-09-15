import React, { createContext, useContext, useState, useEffect } from 'react';

const FinancialContext = createContext(null);

export function FinancialProvider({ children }) {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const resp = await fetch('/api/history?limit=20');
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
        const normalized = {
          ...data,
          intent: data.asset_type === 'stock' ? 'STOCK_ANALYSIS' : 'CRYPTO_ANALYSIS',
        };
        setResult(normalized);
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
      if (!resp.ok || data.success === false) {
        setError(data.detail || data.error || 'Query interpretation request failed.');
        setResult(data);
      } else {
        // Flatten nested analysis structure from POST /api/query
        const analysisBody = data.analysis || {};
        const normalized = {
          ...analysisBody,
          success: true,
          query: data.query,
          intent: data.interpreted?.intent || data.intent,
          interpreted: data.interpreted,
          asset: analysisBody.asset || data.interpreted?.asset || data.asset,
          asset_type: analysisBody.asset_type || data.interpreted?.asset_type || data.asset_type,
          agents_used: data.agents_used || analysisBody.agents_used || [],
          agent_activity: data.agent_activity || analysisBody.agent_activity || [],
          saved_analysis_id: data.saved_analysis_id,
        };

        setResult(normalized);
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
            intent: record.asset_type === 'stock' ? 'STOCK_ANALYSIS' : 'CRYPTO_ANALYSIS',
            agent_activity: record.agent_activity || [],
            agents_used: (record.agent_activity || []).map((a) => a.agent),
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

  const agentActivity = result?.agent_activity || [];

  const analysisContext = result ? {
    query: result.query || (result.asset ? `Analyze ${result.asset}` : null),
    asset: result.asset || result.market_data?.symbol,
    asset_type: result.asset_type,
    intent: result.intent,
    recommendation: result.recommendation?.recommendation,
    recommendation_score: result.recommendation?.recommendation_score,
    confidence: result.recommendation?.confidence,
    risk_level: result.risk_data?.risk_level,
    risk_score: result.risk_data?.risk_score,
    saved_id: result.saved_analysis_id,
  } : null;

  return (
    <FinancialContext.Provider
      value={{
        result,
        history,
        loading,
        historyLoading,
        selectedId,
        error,
        agentActivity,
        analysisContext,
        handleStructuredAnalyze,
        handleQueryAnalyze,
        handleSelectHistoryRecord,
        fetchHistory,
        setError,
      }}
    >
      {children}
    </FinancialContext.Provider>
  );
}

export function useFinancial() {
  const context = useContext(FinancialContext);
  if (!context) {
    throw new Error('useFinancial must be used within a FinancialProvider');
  }
  return context;
}
