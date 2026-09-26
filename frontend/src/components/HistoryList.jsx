import React, { useState } from 'react';
import { History, RefreshCw, Eye, Database, FileText } from 'lucide-react';
import ExportReportModal from './ExportReportModal';

export default function HistoryList({ history, selectedId, onSelectRecord, onRefresh, loading }) {
  const [exportModalRecord, setExportModalRecord] = useState(null);

  if (!history || history.length === 0) {
    return (
      <div className="card">
        <div className="card-title" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <History size={20} color="#3b82f6" />
            Analysis History Log (SQLite Database)
          </div>
          <button
            onClick={onRefresh}
            className="tab-btn"
            disabled={loading}
            style={{ padding: '0.45rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem', flexGrow: 0 }}
          >
            <RefreshCw size={14} className={loading ? 'spinner' : ''} />
            {loading ? 'Refreshing...' : 'Refresh History'}
          </button>
        </div>
        <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
          <Database size={32} style={{ marginBottom: '0.75rem', opacity: 0.5 }} />
          <p style={{ fontSize: '0.95rem' }}>No saved analysis records found in database yet.</p>
          <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>Run an asset analysis or natural language query above to populate history.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-title" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <History size={20} color="#3b82f6" />
          Recent Saved Analyses (SQLite Database)
        </div>
        <button
          onClick={onRefresh}
          className="tab-btn"
          disabled={loading}
          style={{ padding: '0.45rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem', flexGrow: 0 }}
        >
          <RefreshCw size={14} className={loading ? 'spinner' : ''} />
          {loading ? 'Refreshing...' : 'Refresh History'}
        </button>
      </div>

      <div className="table-container">
        <table className="history-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Asset</th>
              <th>Type</th>
              <th>Query Prompt</th>
              <th>Recommendation</th>
              <th>Risk Level</th>
              <th>Sentiment</th>
              <th>Created Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => {
              const rec = (item.recommendation || 'hold').toLowerCase();
              const badgeClass = rec === 'buy' ? 'badge-buy' : rec === 'avoid' ? 'badge-avoid' : 'badge-hold';
              const isSelected = selectedId === item.id;
              const createdDate = item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent';

              return (
                <tr
                  key={item.id}
                  onClick={() => onSelectRecord(item.id)}
                  style={{ backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.15)' : undefined }}
                >
                  <td style={{ fontWeight: 700 }}>#{item.id}</td>
                  <td style={{ fontWeight: 700 }}>{item.asset?.toUpperCase()}</td>
                  <td><span className="badge badge-conf">{item.asset_type?.toUpperCase()}</span></td>
                  <td style={{ maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.query}
                  </td>
                  <td>
                    <span className={`badge ${badgeClass}`}>{rec.toUpperCase()}</span>
                  </td>
                  <td>
                    <span style={{ color: item.risk_level === 'high' ? 'var(--red-avoid)' : item.risk_level === 'low' ? 'var(--green-buy)' : 'var(--amber-hold)', fontWeight: 600 }}>
                      {item.risk_level?.toUpperCase() || '-'} ({item.risk_score ?? '-'})
                    </span>
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{item.news_sentiment || '-'}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{createdDate}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.35rem' }}>
                      <button
                        className="tab-btn"
                        style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectRecord(item.id);
                        }}
                      >
                        <Eye size={13} /> View
                      </button>
                      <button
                        className="tab-btn"
                        style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.25rem', backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', borderColor: 'rgba(59, 130, 246, 0.4)' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setExportModalRecord(item);
                        }}
                      >
                        <FileText size={13} /> Export
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <ExportReportModal
        isOpen={Boolean(exportModalRecord)}
        onClose={() => setExportModalRecord(null)}
        analysis={exportModalRecord}
      />
    </div>
  );
}