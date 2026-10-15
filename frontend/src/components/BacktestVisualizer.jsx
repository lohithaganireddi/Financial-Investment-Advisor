import React, { useState, useEffect } from 'react';
import { authenticatedFetch } from '../services/apiClient';
import {
  TrendingUp,
  ShieldAlert,
  BarChart2,
  DollarSign,
  Clock,
  Play,
  CheckCircle,
  AlertTriangle,
  Info,
  RefreshCw
} from 'lucide-react';

export default function BacktestVisualizer({ initialAsset = 'AAPL', initialAssetType = 'stock', riskScore = null }) {
  const [asset, setAsset] = useState(initialAsset);
  const [assetType, setAssetType] = useState(initialAssetType);
  const [investment, setInvestment] = useState(10000);
  const [horizonMonths, setHorizonMonths] = useState(12);
  const [loading, setLoading] = useState(false);
  const [backtestResult, setBacktestResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialAsset) {
      setAsset(initialAsset);
      setAssetType(initialAssetType || 'stock');
    }
  }, [initialAsset, initialAssetType]);

  // Auto-run initial backtest when asset changes
  useEffect(() => {
    runBacktest();
  }, [initialAsset]);

  const runBacktest = async () => {
    if (!asset) return;
    setLoading(true);
    setError(null);

    try {
      const resp = await authenticatedFetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          asset,
          asset_type: assetType,
          initial_investment: Number(investment),
          horizon_months: Number(horizonMonths),
          iterations: 500,
          risk_score: riskScore !== null ? Number(riskScore) : null,
          seed: 42,
        }),
      });

      const data = await resp.json();
      if (!resp.ok) {
        setError(data.detail || data.error || 'Monte Carlo backtest simulation failed.');
      } else {
        setBacktestResult(data);
      }
    } catch (err) {
      setError(`Failed to execute backtest simulation: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const metrics = backtestResult?.metrics;
  const trajectory = backtestResult?.trajectory || [];

  return (
    <div className="card" style={{ border: '1px solid rgba(59, 130, 246, 0.3)', background: 'linear-gradient(135deg, rgba(21, 29, 48, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)' }}>
      <div className="card-title">
        <BarChart2 size={20} color="#3b82f6" />
        Interactive Monte Carlo Portfolio Stress-Test & Backtesting
      </div>

      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
        Statistical Monte Carlo projection evaluating 500 stochastic trials, percentile outcomes, Value at Risk (VaR 95%), and maximum expected drawdown.
      </p>

      {/* Control Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem', background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
        <div>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Target Asset Symbol</label>
          <input
            type="text"
            value={asset}
            onChange={(e) => setAsset(e.target.value.toUpperCase())}
            style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-color)', color: 'var(--text-main)', padding: '0.4rem 0.6rem', borderRadius: '6px', fontSize: '0.9rem', outline: 'none' }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Initial Capital ($ USD)</label>
          <select
            value={investment}
            onChange={(e) => setInvestment(Number(e.target.value))}
            style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-color)', color: 'var(--text-main)', padding: '0.4rem 0.6rem', borderRadius: '6px', fontSize: '0.9rem', outline: 'none' }}
          >
            <option value={1000}>$1,000 USD</option>
            <option value={5000}>$5,000 USD</option>
            <option value={10000}>$10,000 USD</option>
            <option value={25000}>$25,000 USD</option>
            <option value={50000}>$50,000 USD</option>
            <option value={100000}>$100,000 USD</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Time Horizon (Months)</label>
          <select
            value={horizonMonths}
            onChange={(e) => setHorizonMonths(Number(e.target.value))}
            style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-color)', color: 'var(--text-main)', padding: '0.4rem 0.6rem', borderRadius: '6px', fontSize: '0.9rem', outline: 'none' }}
          >
            <option value={3}>3 Months (Short-term)</option>
            <option value={6}>6 Months (Mid-term)</option>
            <option value={12}>12 Months (1 Year)</option>
            <option value={24}>24 Months (2 Years)</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button
            onClick={runBacktest}
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', padding: '0.5rem 1rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 6, fontSize: '0.85rem' }}
          >
            {loading ? <RefreshCw size={14} className="spin" /> : <Play size={14} />}
            Run Simulation
          </button>
        </div>
      </div>

      {error && (
        <div className="info-box" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171', marginBottom: '1.25rem' }}>
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Results Grid */}
      {metrics && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="hero-metric-box" style={{ borderColor: 'rgba(16, 185, 129, 0.4)' }}>
              <div className="hero-metric-label">Expected Final Value (P50)</div>
              <div className="hero-metric-val" style={{ color: '#34d399' }}>
                ${metrics.expected_final_value?.toLocaleString()}
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4, color: metrics.expected_return_pct >= 0 ? '#10b981' : '#ef4444' }}>
                {metrics.expected_return_pct >= 0 ? `+${metrics.expected_return_pct}%` : `${metrics.expected_return_pct}%`} Return
              </div>
            </div>

            <div className="hero-metric-box" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
              <div className="hero-metric-label">Value at Risk (VaR 95%)</div>
              <div className="hero-metric-val" style={{ color: '#ef4444' }}>
                ${metrics.value_at_risk_95?.toLocaleString()}
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>95% Max Capital at Loss</div>
            </div>

            <div className="hero-metric-box">
              <div className="hero-metric-label">Sharpe Ratio</div>
              <div className="hero-metric-val" style={{ color: metrics.sharpe_ratio >= 1.0 ? '#10b981' : '#f59e0b' }}>
                {metrics.sharpe_ratio}
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>Risk-Adjusted Efficiency</div>
            </div>

            <div className="hero-metric-box">
              <div className="hero-metric-label">Max Projected Drawdown</div>
              <div className="hero-metric-val" style={{ color: '#f59e0b' }}>
                -{metrics.max_drawdown_pct}%
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>Peak-to-Trough Decline</div>
            </div>

            <div className="hero-metric-box">
              <div className="hero-metric-label">Profitable Trials Ratio</div>
              <div className="hero-metric-val" style={{ color: '#3b82f6' }}>
                {metrics.success_rate_pct}%
              </div>
              <div className="hero-metric-label" style={{ fontSize: '0.7rem', marginTop: 4 }}>Positive Gain Probability</div>
            </div>
          </div>

          {/* Percentile Scenario Comparison Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '1rem', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.8rem', color: '#ef4444', fontWeight: 700, marginBottom: 4 }}>BEARISH / STRESS SCENARIO (5th Percentile)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                ${metrics.bearish_p5_value?.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                Severe downside market correction path.
              </div>
            </div>

            <div style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '1rem', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.8rem', color: '#60a5fa', fontWeight: 700, marginBottom: 4 }}>MEDIAN EXPECTED SCENARIO (50th Percentile)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                ${metrics.expected_final_value?.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                Expected stochastic baseline trajectory.
              </div>
            </div>

            <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1rem', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 700, marginBottom: 4 }}>BULLISH SCENARIO (95th Percentile)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                ${metrics.bullish_p95_value?.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                Optimistic high-growth path.
              </div>
            </div>
          </div>

          {/* Monthly Trajectory Progress Bars */}
          {trajectory.length > 0 && (
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
                Monthly Projected Capital Trajectory ($ USD)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '220px', overflowY: 'auto' }}>
                {trajectory.map((pt) => (
                  <div key={pt.month} style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                    <span style={{ width: '60px', color: 'var(--text-muted)' }}>Month {pt.month}</span>
                    <div style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ color: '#ef4444', width: '90px' }}>P5: ${pt.p5?.toLocaleString()}</span>
                      <span style={{ color: '#60a5fa', width: '90px', fontWeight: 700 }}>P50: ${pt.p50?.toLocaleString()}</span>
                      <span style={{ color: '#34d399', width: '90px' }}>P95: ${pt.p95?.toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="disclaimer-box">
            <Info size={14} />
            <span>{backtestResult.disclaimer}</span>
          </div>
        </>
      )}
    </div>
  );
}
