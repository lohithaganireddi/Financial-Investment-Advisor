import React, { useState } from 'react';
import { Newspaper, Search, Sparkles, AlertCircle, ExternalLink, Globe } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';

export default function FinancialNews() {
  const { result, loading, handleQueryAnalyze } = useFinancial();
  const [newsQuery, setNewsQuery] = useState('market news');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const clean = newsQuery.trim();
    if (!clean) {
      setErrorMsg('Please enter a topic or asset for financial news.');
      return;
    }
    setErrorMsg('');
    handleQueryAnalyze({ query: `${clean} news` });
  };

  const handleQuickNews = (topic) => {
    setNewsQuery(topic);
    setErrorMsg('');
    handleQueryAnalyze({ query: `${topic} news` });
  };

  const newsData = result?.news_data || result?.analysis?.news_data;
  const articles = newsData?.articles || newsData?.top_headlines || [];
  const sentiment = newsData?.overall_sentiment || 'neutral';

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <Newspaper size={24} color="#10b981" />
            Financial News & Market Sentiment
          </h2>
          <p className="page-subtitle">
            Gather market headlines, breaking story sentiment, and global news coverage.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <Sparkles size={18} color="#10b981" />
          Search News & Headlines
        </div>

        {errorMsg && (
          <div className="error-box" style={{ marginBottom: '1rem' }}>
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">News Topic / Asset Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Apple, Bitcoin, Federal Reserve, Stock market"
              value={newsQuery}
              onChange={(e) => { setNewsQuery(e.target.value); setErrorMsg(''); }}
              disabled={loading}
              required
            />
          </div>

          <div className="preset-bar">
            <span className="preset-label">Quick Topics:</span>
            <button type="button" className="preset-chip" onClick={() => handleQuickNews('General Market')}>
              General Market
            </button>
            <button type="button" className="preset-chip" onClick={() => handleQuickNews('Apple')}>
              Apple News
            </button>
            <button type="button" className="preset-chip" onClick={() => handleQuickNews('Bitcoin')}>
              Bitcoin News
            </button>
            <button type="button" className="preset-chip" onClick={() => handleQuickNews('Federal Reserve')}>
              Federal Reserve
            </button>
          </div>

          <button type="submit" className="btn-primary" style={{ backgroundColor: '#10b981' }} disabled={loading}>
            <Search size={18} />
            {loading ? 'Fetching News Data...' : 'Search Financial News'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="card loading-box">
          <div className="spinner"></div>
          <div>
            <strong>Financial News Agent active...</strong>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Gathering news headlines and calculating sentiment metrics.
            </p>
          </div>
        </div>
      )}

      {!loading && newsData && (
        <div className="card">
          <div className="news-header-row">
            <div>
              <h3 className="card-title" style={{ marginBottom: 4 }}>
                <Globe size={18} color="#10b981" />
                Market News Summary
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Query: "{result.query || newsQuery}"
              </p>
            </div>
            <div className={`sentiment-badge sentiment-${sentiment.toLowerCase()}`}>
              Sentiment: {sentiment.toUpperCase()}
            </div>
          </div>

          {articles.length > 0 ? (
            <div className="article-grid">
              {articles.map((art, idx) => (
                <div key={idx} className="article-card">
                  <h4 className="article-title">{art.title}</h4>
                  {art.description && <p className="article-desc">{art.description}</p>}
                  <div className="article-meta">
                    <span>{art.source || 'NewsData API'}</span>
                    {art.url && (
                      <a href={art.url} target="_blank" rel="noopener noreferrer" className="article-link">
                        Read Story <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="info-box" style={{ marginTop: '1rem' }}>
              No detailed article links were returned for this topic, but sentiment was evaluated as <strong>{sentiment}</strong>.
            </div>
          )}
        </div>
      )}

      {!loading && !newsData && (
        <div className="card empty-state-card">
          <Newspaper size={44} color="#10b981" style={{ opacity: 0.6 }} />
          <h3>No News Results Loaded</h3>
          <p>
            Use the search box above to fetch live financial news, article headlines, and market sentiment.
          </p>
        </div>
      )}
    </div>
  );
}
