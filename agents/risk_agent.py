"""
Risk Analysis Agent Module

This module implements the RiskAgent, which evaluates financial risk based on structured
output produced by StockAgent or CryptoAgent. It uses a deterministic scoring formula
to classify risk as low, medium, or high without making any external API calls.

Risk Scoring Rules:
    Base score:
        - StockAgent input  -> 30
        - CryptoAgent input -> 50

    Movement adjustment (based on absolute percentage change):
        - |change| <= 2%           -> +0
        - |change| > 2% and <= 5%  -> +15
        - |change| > 5%            -> +30

    Market direction adjustment:
        - bullish -> +0
        - neutral -> +10
        - bearish -> +20

    Crypto asset bonus:
        - CryptoAgent input -> +10  (added on top of the crypto base)

    Score is capped at 100.

    Risk level classification:
        - 0  to 39  -> "low"
        - 40 to 69  -> "medium"
        - 70 to 100 -> "high"
"""

from typing import Any, Dict


class RiskAgent:
    """Deterministic risk analysis agent for evaluating StockAgent and CryptoAgent outputs."""

    # -----------------------------------------------------------------------
    # Supported upstream agents and their configuration
    # -----------------------------------------------------------------------
    _AGENT_CONFIG: Dict[str, Dict[str, Any]] = {
        "StockAgent": {
            "asset_type": "stock",
            "base_score": 30,
            "pct_field": "change_percent",      # float in StockAgent output
            "asset_field": "symbol",
        },
        "CryptoAgent": {
            "asset_type": "crypto",
            "base_score": 50,
            "pct_field": "change_percent_24h",  # float in CryptoAgent output
            "asset_field": "coin_id",
        },
    }

    # -----------------------------------------------------------------------
    # Risk level thresholds
    # -----------------------------------------------------------------------
    _LOW_THRESHOLD = 40      # below this -> "low"
    _HIGH_THRESHOLD = 70     # at or above this -> "high"
    _SCORE_CAP = 100

    def _parse_percentage(self, raw: Any) -> float:
        """
        Safely parse a percentage value into a float.
        Handles both numeric types and strings like '1.3736%' or '-2.5%'.
        Returns 0.0 for any value that cannot be parsed.
        """
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, str):
            cleaned = raw.replace("%", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        return 0.0

    def _movement_score(self, abs_pct: float) -> int:
        """
        Return the movement adjustment for the given absolute percentage change.
            |pct| <= 2%          -> +0
            2% < |pct| <= 5%     -> +15
            |pct| > 5%           -> +30
        """
        if abs_pct <= 2.0:
            return 0
        elif abs_pct <= 5.0:
            return 15
        else:
            return 30

    def _direction_score(self, market_direction: str) -> int:
        """
        Return the direction adjustment for the given market direction string.
            bullish -> +0
            neutral -> +10
            bearish -> +20
        """
        return {"bullish": 0, "neutral": 10, "bearish": 20}.get(market_direction, 0)

    def _risk_level(self, score: int) -> str:
        """Classify a numeric risk score into a human-readable risk level string."""
        if score < self._LOW_THRESHOLD:
            return "low"
        elif score < self._HIGH_THRESHOLD:
            return "medium"
        else:
            return "high"

    def analyze_risk(self, data: dict) -> dict:
        """
        Analyze financial risk from a StockAgent or CryptoAgent result dictionary.

        :param data: The structured output dict returned by StockAgent.analyze_stock()
                     or CryptoAgent.analyze_crypto().
        :return: Structured dictionary containing the risk score, risk level, and
                 a breakdown of all scoring components, or an error dict on failure.
        """
        # --- Validate: input must be a non-empty dict ----------------------
        if not isinstance(data, dict):
            return {
                "success": False,
                "agent": "RiskAgent",
                "error": "Input must be a dictionary (StockAgent or CryptoAgent output)."
            }

        if not data:
            return {
                "success": False,
                "agent": "RiskAgent",
                "error": "Input dictionary is empty. Provide a valid agent result."
            }

        # --- Validate: upstream agent must have succeeded ------------------
        if not data.get("success"):
            return {
                "success": False,
                "agent": "RiskAgent",
                "error": "Upstream agent reported failure. Cannot assess risk on failed data."
            }

        # --- Validate: identify which upstream agent produced this data ----
        upstream_agent = data.get("agent")
        if not upstream_agent or upstream_agent not in self._AGENT_CONFIG:
            return {
                "success": False,
                "agent": "RiskAgent",
                "error": (
                    f"Unsupported or missing upstream agent: '{upstream_agent}'. "
                    f"Supported agents: {list(self._AGENT_CONFIG.keys())}."
                )
            }

        config = self._AGENT_CONFIG[upstream_agent]
        asset_type = config["asset_type"]
        base_score = config["base_score"]
        pct_field = config["pct_field"]
        asset_field = config["asset_field"]

        # --- Retrieve asset identifier -------------------------------------
        asset = data.get(asset_field)
        if not asset:
            return {
                "success": False,
                "agent": "RiskAgent",
                "error": f"Missing asset identifier field '{asset_field}' in upstream data."
            }

        # --- Retrieve and validate the percentage change -------------------
        raw_pct = data.get(pct_field)
        if raw_pct is None:
            return {
                "success": False,
                "agent": "RiskAgent",
                "error": f"Missing percentage field '{pct_field}' in upstream data."
            }

        # Detect unparseable string values before accepting 0.0 fallback
        if isinstance(raw_pct, str):
            cleaned = raw_pct.replace("%", "").strip()
            try:
                float(cleaned)
            except ValueError:
                return {
                    "success": False,
                    "agent": "RiskAgent",
                    "error": f"Cannot parse percentage value: '{raw_pct}'."
                }

        change_pct = self._parse_percentage(raw_pct)

        # --- Retrieve market direction (default to neutral if absent) ------
        market_direction = str(data.get("market_direction", "neutral")).lower()

        # --- Compute risk score --------------------------------------------
        abs_pct = abs(change_pct)

        move_adjustment = self._movement_score(abs_pct)
        direction_adjustment = self._direction_score(market_direction)
        # Crypto assets carry an additional volatility premium
        crypto_bonus = 10 if asset_type == "crypto" else 0

        raw_score = base_score + move_adjustment + direction_adjustment + crypto_bonus
        final_score = min(raw_score, self._SCORE_CAP)

        level = self._risk_level(final_score)

        # --- Build analysis summary ----------------------------------------
        analysis_text = (
            f"{asset.upper()} ({asset_type}) risk score is {final_score}/100, "
            f"classified as {level} risk. "
            f"Market direction: {market_direction}. "
            f"24h movement: {change_pct:+.2f}%."
        )

        return {
            "success": True,
            "agent": "RiskAgent",
            "asset": asset,
            "asset_type": asset_type,
            "risk_score": final_score,
            "risk_level": level,
            "market_direction": market_direction,
            "change_percent": change_pct,
            "analysis": analysis_text,
            "score_breakdown": {
                "base_score": base_score,
                "movement_adjustment": move_adjustment,
                "direction_adjustment": direction_adjustment,
                "crypto_bonus": crypto_bonus,
                "raw_score": raw_score,
                "capped_at": self._SCORE_CAP
            }
        }
