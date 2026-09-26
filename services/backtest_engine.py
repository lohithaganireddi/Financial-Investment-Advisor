"""
Portfolio Backtest & Monte Carlo Simulation Engine Module

Provides deterministic Monte Carlo price path simulation and historical scenario backtesting
for equity and cryptocurrency portfolios. Evaluates projected portfolio outcomes, percentile
scenarios (5th, 50th, 95th percentiles), Value at Risk (VaR 95%), Sharpe Ratio, Maximum Drawdown,
and success probabilities.
"""

import math
import random
from typing import Any, Dict, List, Optional


class BacktestEngine:
    """
    Monte Carlo Simulation & Backtesting Engine for Portfolio Analysis.

    Executes lognormal asset price random walk simulations to project portfolio performance
    over a specified time horizon.
    """

    # Baseline asset return and volatility parameters
    _DEFAULT_STOCK_ANNUAL_RETURN = 0.10   # 10% expected annual return
    _DEFAULT_STOCK_ANNUAL_VOL = 0.20      # 20% annual volatility
    _DEFAULT_CRYPTO_ANNUAL_RETURN = 0.18  # 18% expected annual return
    _DEFAULT_CRYPTO_ANNUAL_VOL = 0.55     # 55% annual volatility
    _RISK_FREE_RATE = 0.03                 # 3% annual risk-free rate for Sharpe ratio calculation

    _DISCLAIMER = (
        "Software-generated Monte Carlo simulation for educational stress-testing purposes. "
        "Past performance and mathematical projections do not guarantee future financial results."
    )

    def run_backtest(
        self,
        asset: str,
        asset_type: str = "stock",
        initial_investment: float = 10000.0,
        horizon_months: int = 12,
        iterations: int = 500,
        risk_score: Optional[int] = None,
        seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        """
        Execute Monte Carlo simulation backtest for a target asset portfolio.

        :param asset: Asset ticker symbol or coin ID (e.g., 'AAPL', 'BTC').
        :param asset_type: 'stock' or 'crypto'.
        :param initial_investment: Starting dollar amount (must be > 0).
        :param horizon_months: Simulation horizon in months (1 to 60).
        :param iterations: Number of statistical trials (10 to 2000).
        :param risk_score: Optional 0-100 volatility risk score to adjust simulation parameters.
        :param seed: Optional integer seed for 100% reproducible pseudo-random simulations.
        :return: Standardized dictionary containing metrics, percentile trajectories, and summary.
        """
        # --- Validate Inputs ------------------------------------------------
        if not asset or not isinstance(asset, str):
            return {"success": False, "error": "Asset symbol or name must be a non-empty string."}

        try:
            initial_investment = float(initial_investment)
            if initial_investment <= 0:
                return {"success": False, "error": "Initial investment must be greater than 0."}
        except (ValueError, TypeError):
            return {"success": False, "error": "Initial investment must be a valid positive number."}

        try:
            horizon_months = int(horizon_months)
            if horizon_months < 1 or horizon_months > 60:
                return {"success": False, "error": "Horizon months must be between 1 and 60."}
        except (ValueError, TypeError):
            return {"success": False, "error": "Horizon months must be an integer between 1 and 60."}

        try:
            iterations = int(iterations)
            if iterations < 10 or iterations > 2000:
                return {"success": False, "error": "Iterations must be an integer between 10 and 2000."}
        except (ValueError, TypeError):
            return {"success": False, "error": "Iterations must be an integer between 10 and 2000."}

        clean_type = str(asset_type).lower() if asset_type else "stock"
        if clean_type not in ("stock", "crypto"):
            clean_type = "stock"

        # Set random seed if provided for reproducible testing
        rng = random.Random(seed) if seed is not None else random.Random()

        # --- Derive Return & Volatility Parameters --------------------------
        if clean_type == "crypto":
            mu_annual = self._DEFAULT_CRYPTO_ANNUAL_RETURN
            sigma_annual = self._DEFAULT_CRYPTO_ANNUAL_VOL
        else:
            mu_annual = self._DEFAULT_STOCK_ANNUAL_RETURN
            sigma_annual = self._DEFAULT_STOCK_ANNUAL_VOL

        # Adjust volatility based on RiskAgent risk score if supplied (0 to 100)
        if risk_score is not None and isinstance(risk_score, (int, float)):
            clamped_risk = max(0, min(float(risk_score), 100.0))
            # Scale volatility factor: risk_score 50 = 1.0x, risk_score 100 = 1.5x, risk_score 0 = 0.7x
            vol_multiplier = 0.7 + (clamped_risk / 100.0) * 0.8
            sigma_annual = sigma_annual * vol_multiplier

        dt = 1.0 / 12.0  # Monthly time step in years
        drift_monthly = (mu_annual - 0.5 * (sigma_annual ** 2)) * dt
        vol_monthly = sigma_annual * math.sqrt(dt)

        # --- Execute Monte Carlo Simulation ---------------------------------
        # All simulated trajectories: list of lists, where each inner list has (horizon_months + 1) values
        all_trials: List[List[float]] = []

        for _ in range(iterations):
            path = [initial_investment]
            curr_val = initial_investment
            for _m in range(horizon_months):
                z = rng.gauss(0.0, 1.0)
                # Geometric Brownian Motion step
                growth_factor = math.exp(drift_monthly + vol_monthly * z)
                curr_val = curr_val * growth_factor
                path.append(curr_val)
            all_trials.append(path)

        # --- Compute Monthly Percentiles ------------------------------------
        # For each month 0..horizon_months, sort values across all trials
        monthly_percentiles: List[Dict[str, float]] = []

        for m in range(horizon_months + 1):
            month_vals = sorted([trial[m] for trial in all_trials])
            p5_idx = int(0.05 * (iterations - 1))
            p50_idx = int(0.50 * (iterations - 1))
            p95_idx = int(0.95 * (iterations - 1))

            monthly_percentiles.append({
                "month": m,
                "p5": round(month_vals[p5_idx], 2),
                "p50": round(month_vals[p50_idx], 2),
                "p95": round(month_vals[p95_idx], 2),
            })

        # --- Compute Summary Metrics ----------------------------------------
        final_values = sorted([trial[-1] for trial in all_trials])
        p5_final = final_values[int(0.05 * (iterations - 1))]
        p50_final = final_values[int(0.50 * (iterations - 1))]
        p95_final = final_values[int(0.95 * (iterations - 1))]

        expected_return_pct = round(((p50_final - initial_investment) / initial_investment) * 100.0, 2)
        var_95 = round(max(0.0, initial_investment - p5_final), 2)
        sharpe = round((mu_annual - self._RISK_FREE_RATE) / sigma_annual, 2)

        # Calculate max drawdown across median trajectory
        max_drawdown_pct = 0.0
        peak = initial_investment
        for pt in monthly_percentiles:
            val = pt["p50"]
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100.0
            if dd > max_drawdown_pct:
                max_drawdown_pct = dd
        max_drawdown_pct = round(max_drawdown_pct, 2)

        # Count profitable trials
        profitable_trials = sum(1 for v in final_values if v >= initial_investment)
        success_rate_pct = round((profitable_trials / iterations) * 100.0, 1)

        summary = (
            f"Monte Carlo simulation of {iterations} trials for {asset.upper()} over {horizon_months} months "
            f"projects a median outcome of ${round(p50_final, 2):,.2f} ({expected_return_pct:+.2f}%) "
            f"with a 95% Value at Risk (VaR) of ${var_95:,.2f}."
        )

        return {
            "success": True,
            "asset": asset.upper(),
            "asset_type": clean_type,
            "initial_investment": round(initial_investment, 2),
            "horizon_months": horizon_months,
            "iterations": iterations,
            "metrics": {
                "expected_final_value": round(p50_final, 2),
                "expected_return_pct": expected_return_pct,
                "bearish_p5_value": round(p5_final, 2),
                "bullish_p95_value": round(p95_final, 2),
                "volatility_pct": round(sigma_annual * 100.0, 2),
                "max_drawdown_pct": max_drawdown_pct,
                "value_at_risk_95": var_95,
                "sharpe_ratio": sharpe,
                "success_rate_pct": success_rate_pct,
            },
            "trajectory": monthly_percentiles,
            "summary": summary,
            "disclaimer": self._DISCLAIMER,
        }
