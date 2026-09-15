import React from 'react';
import { History } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import HistoryList from '../components/HistoryList';
import ResultCard from '../components/ResultCard';

export default function AnalysisHistory() {
  const {
    history,
    selectedId,
    handleSelectHistoryRecord,
    fetchHistory,
    historyLoading,
    result,
    loading,
  } = useFinancial();

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <History size={24} color="#3b82f6" />
            Analysis History Log
          </h2>
          <p className="page-subtitle">
            Browse and inspect historical multi-agent analyses persisted in SQLite database storage.
          </p>
        </div>
      </div>

      <HistoryList
        history={history}
        selectedId={selectedId}
        onSelectRecord={handleSelectHistoryRecord}
        onRefresh={fetchHistory}
        loading={historyLoading}
      />

      {result && !loading && selectedId && (
        <div style={{ marginTop: '2rem' }}>
          <div className="section-title">
            <span>Inspecting Historical Record #{selectedId}</span>
          </div>
          <ResultCard result={result} />
        </div>
      )}
    </div>
  );
}
