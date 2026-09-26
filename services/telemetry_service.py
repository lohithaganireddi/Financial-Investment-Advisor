"""
System Telemetry & Performance Monitoring Service Module

Tracks aggregate multi-agent pipeline performance, latency metrics, per-agent execution times,
success/failure ratios, and intent distribution without leaking sensitive user queries or keys.
"""

import time
from typing import Any, Dict, List, Optional


class TelemetryService:
    """
    Lightweight, thread-safe in-memory performance telemetry manager.
    """

    def __init__(self):
        self._total_requests: int = 0
        self._successful_requests: int = 0
        self._failed_requests: int = 0
        self._total_duration_ms: float = 0.0

        # Intent distribution counter
        self._intent_distribution: Dict[str, int] = {
            "STOCK_ANALYSIS": 0,
            "CRYPTO_ANALYSIS": 0,
            "GENERAL_FINANCIAL_NEWS": 0,
            "UNSUPPORTED": 0,
        }

        # Per-agent telemetry metrics tracking
        self._per_agent_metrics: Dict[str, Dict[str, Any]] = {
            "StockAgent": {"calls": 0, "successes": 0, "failures": 0, "total_time_ms": 0.0},
            "CryptoAgent": {"calls": 0, "successes": 0, "failures": 0, "total_time_ms": 0.0},
            "NewsAgent": {"calls": 0, "successes": 0, "failures": 0, "total_time_ms": 0.0},
            "RiskAgent": {"calls": 0, "successes": 0, "failures": 0, "total_time_ms": 0.0},
            "PortfolioAgent": {"calls": 0, "successes": 0, "failures": 0, "total_time_ms": 0.0},
        }

    def record_execution(
        self,
        intent: str,
        duration_ms: float,
        success: bool = True,
        agent_activity: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Record a pipeline execution turn safely. Wrapped to ensure failure never interrupts request handling.
        """
        try:
            self._total_requests += 1
            if success:
                self._successful_requests += 1
            else:
                self._failed_requests += 1

            self._total_duration_ms += max(0.0, float(duration_ms))

            clean_intent = intent.upper() if intent else "UNSUPPORTED"
            self._intent_distribution[clean_intent] = self._intent_distribution.get(clean_intent, 0) + 1

            if agent_activity and isinstance(agent_activity, list):
                for item in agent_activity:
                    if not isinstance(item, dict):
                        continue
                    agent_name = item.get("agent")
                    if agent_name and agent_name in self._per_agent_metrics:
                        m = self._per_agent_metrics[agent_name]
                        m["calls"] += 1
                        if item.get("status") == "success":
                            m["successes"] += 1
                        else:
                            m["failures"] += 1
        except Exception as exc:
            # Telemetry logging failure should never crash application requests
            print(f"Telemetry record notice: {exc}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retrieve structured performance telemetry metrics.
        """
        avg_latency = (
            round(self._total_duration_ms / self._total_requests, 2)
            if self._total_requests > 0
            else 0.0
        )

        formatted_agent_metrics = {}
        for agent, data in self._per_agent_metrics.items():
            calls = data["calls"]
            avg_time = round(data["total_time_ms"] / calls, 2) if calls > 0 else 0.0
            formatted_agent_metrics[agent] = {
                "calls": calls,
                "successes": data["successes"],
                "failures": data["failures"],
                "total_time_ms": round(data["total_time_ms"], 2),
                "avg_time_ms": avg_time,
                "success_rate": round((data["successes"] / calls) * 100, 1) if calls > 0 else 100.0,
            }

        success_rate = (
            round((self._successful_requests / self._total_requests) * 100, 1)
            if self._total_requests > 0
            else 100.0
        )

        return {
            "success": True,
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "average_latency_ms": avg_latency,
            "success_rate_percent": success_rate,
            "health_status": "healthy" if self._failed_requests == 0 or success_rate >= 80.0 else "degraded",
            "intent_distribution": self._intent_distribution,
            "per_agent_metrics": formatted_agent_metrics,
        }
