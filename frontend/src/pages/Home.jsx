import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  TrendingUp,
  Coins,
  Newspaper,
  ShieldAlert,
  Briefcase,
  Bot,
  ArrowRight,
  PieChart,
} from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import AnalysisForm from '../components/AnalysisForm';
import ResultCard from '../components/ResultCard';
import HistoryList from '../components/HistoryList';
import LiveTickerStream from '../components/LiveTickerStream';

export default function Home() {
  const {
    result,
    history,
    loading,
    historyLoading,
    selectedId,
    handleStructuredAnalyze,
    handleQueryAnalyze,
    handleSelectHistoryRecord,
    fetchHistory,
  } = useFinancial();

  const featureCards = [
    {
      title: 'Stock Analysis',
      desc: 'Real-time equity market data via Alpha Vantage API.',
      icon: TrendingUp,
      path: '/stocks',
      color: '#3b82f6',
    },
    {
      title: 'Crypto Analysis',
      desc: 'Cryptocurrency market tracking via CoinGecko API.',
      icon: Coins,
      path: '/crypto',
      color: '#8b5cf6',
    },
    {
      title: 'Financial News',
      desc: 'Market headlines and sentiment via NewsData API.',
      icon: Newspaper,
      path: '/news',
      color: '#10b981',
    },
    {
      title: 'Risk Dashboard',
      desc: 'Volatility evaluation, risk scores, and market exposure.',
      icon: ShieldAlert,
      path: '/risk',
      color: '#f59e0b',
    },
    {
      title: 'Portfolio Advisor',
      desc: 'Multi-agent recommendations (BUY / HOLD / AVOID).',
      icon: Briefcase,
      path: '/portfolio',
      color: '#ec4899',
    },
    {
      title: 'Agent Activity',
      desc: 'Step-by-step pipeline execution and telemetry.',
      icon: Bot,
      path: '/agents',
      color: '#06b6d4',
    },
  ];

  return (
    <div className="page-container">
      {/* Hero Welcome Banner */}
      <div className="card hero-card">
        <div className="hero-content">
          <div className="hero-badge">
            <Sparkles size={14} /> Multi-Agent AI Engine
          </div>
          <h2 className="hero-title">SmartFinancial Advisor</h2>
          <p className="hero-subtitle">
            Multi-Agent Financial Intelligence for Smarter Investment Decisions
          </p>
          <p className="hero-description">
            Orchestrating specialized AI agents (Stock, Crypto, Financial News, Volatility Risk, and Portfolio Recommendation) into a unified intelligence pipeline.
          </p>
        </div>
      </div>

      {/* Real-Time WebSocket Ticker Streaming Feed */}
      <LiveTickerStream />

      {/* Analysis Form Component */}
      <AnalysisForm
        onAnalyze={handleStructuredAnalyze}
        onQuery={handleQueryAnalyze}
        loading={loading}
      />

      {/* Active Result Output */}
      {result && !loading && <ResultCard result={result} />}

      {/* Quick Access Feature Cards */}
      <div className="section-title">
        <PieChart size={20} className="section-icon" />
        <span>Financial Intelligence Modules</span>
      </div>

      <div className="feature-grid">
        {featureCards.map((card, idx) => {
          const IconComp = card.icon;
          return (
            <Link key={idx} to={card.path} className="feature-card">
              <div className="feature-card-header">
                <div className="feature-icon" style={{ backgroundColor: `${card.color}15`, color: card.color }}>
                  <IconComp size={22} />
                </div>
                <ArrowRight size={18} className="feature-arrow" />
              </div>
              <h3 className="feature-title">{card.title}</h3>
              <p className="feature-desc">{card.desc}</p>
            </Link>
          );
        })}
      </div>

      {/* Recent History Section */}
      <HistoryList
        history={history}
        selectedId={selectedId}
        onSelectRecord={handleSelectHistoryRecord}
        onRefresh={fetchHistory}
        loading={historyLoading}
      />
    </div>
  );
}
