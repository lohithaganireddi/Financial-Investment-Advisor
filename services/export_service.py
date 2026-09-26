"""
Financial Analysis Report Export Service Module

Provides generation of structured JSON payload exports and print-ready HTML/PDF
financial report documents from multi-agent analysis results.
"""

from datetime import datetime, timezone
import html
from typing import Any, Dict, Optional


class ExportService:
    """
    Export generator service for converting financial analysis records into JSON payloads or HTML reports.
    """

    @staticmethod
    def _safe_str(val: Any, default: str = "N/A") -> str:
        if val is None:
            return default
        return str(val)

    @classmethod
    def generate_json_export(cls, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a clean, structured JSON payload representation of a financial analysis record.
        """
        now_iso = datetime.now(timezone.utc).isoformat()

        # Parse agent activity if present
        agent_activity = analysis.get("agent_activity", [])
        if isinstance(agent_activity, str):
            import json
            try:
                agent_activity = json.loads(agent_activity)
            except Exception:
                agent_activity = []

        return {
            "export_metadata": {
                "system": "SmartFinancial Advisor (FinSight 2.0)",
                "export_timestamp": now_iso,
                "version": "2.0.0",
                "format": "JSON",
            },
            "analysis_record": {
                "id": analysis.get("id"),
                "user_id": analysis.get("user_id"),
                "query": analysis.get("query"),
                "asset": analysis.get("asset"),
                "asset_type": analysis.get("asset_type"),
                "news_query": analysis.get("news_query"),
                "metrics": {
                    "recommendation": analysis.get("recommendation", "N/A"),
                    "recommendation_score": analysis.get("recommendation_score"),
                    "confidence": analysis.get("confidence", "N/A"),
                    "risk_score": analysis.get("risk_score"),
                    "risk_level": analysis.get("risk_level", "N/A"),
                    "market_direction": analysis.get("market_direction", "N/A"),
                    "news_sentiment": analysis.get("news_sentiment", "N/A"),
                },
                "agent_activity": agent_activity,
                "created_at": str(analysis.get("created_at", "")),
            },
            "disclaimer": (
                "This report is generated automatically by SmartFinancial Advisor for informational purposes only. "
                "It does not constitute direct financial advice, investment endorsement, or solicitation."
            )
        }

    @classmethod
    def generate_html_report(cls, analysis: Dict[str, Any]) -> str:
        """
        Generates a print-ready, styled HTML document for financial analysis reports.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        asset = html.escape(cls._safe_str(analysis.get("asset"), "UNKNOWN"))
        asset_type = html.escape(cls._safe_str(analysis.get("asset_type"), "asset").upper())
        query = html.escape(cls._safe_str(analysis.get("query"), "Financial Analysis Query"))
        rec = html.escape(cls._safe_str(analysis.get("recommendation"), "N/A"))
        rec_score = cls._safe_str(analysis.get("recommendation_score"), "N/A")
        confidence = html.escape(cls._safe_str(analysis.get("confidence"), "N/A"))
        risk_score = cls._safe_str(analysis.get("risk_score"), "N/A")
        risk_level = html.escape(cls._safe_str(analysis.get("risk_level"), "N/A"))
        market_dir = html.escape(cls._safe_str(analysis.get("market_direction"), "N/A"))
        sentiment = html.escape(cls._safe_str(analysis.get("news_sentiment"), "N/A"))
        created_at = html.escape(cls._safe_str(analysis.get("created_at"), now_str))

        # Color badges based on recommendation / risk
        rec_color = "#10b981" if "BUY" in rec.upper() else "#ef4444" if "SELL" in rec.upper() else "#f59e0b"
        risk_color = "#ef4444" if "HIGH" in risk_level.upper() else "#10b981" if "LOW" in risk_level.upper() else "#f59e0b"

        # Agent activity formatting
        agent_activity = analysis.get("agent_activity", [])
        if isinstance(agent_activity, str):
            import json
            try:
                agent_activity = json.loads(agent_activity)
            except Exception:
                agent_activity = []

        agent_rows_html = ""
        if isinstance(agent_activity, list) and len(agent_activity) > 0:
            for item in agent_activity:
                if not isinstance(item, dict):
                    continue
                ag_name = html.escape(cls._safe_str(item.get("agent")))
                ag_status = html.escape(cls._safe_str(item.get("status")).upper())
                ag_summary = html.escape(cls._safe_str(item.get("summary")))
                status_color = "#10b981" if ag_status == "SUCCESS" else "#ef4444"
                agent_rows_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">{ag_name}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><span style="color: {status_color}; font-weight: 700;">● {ag_status}</span></td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; color: #475569;">{ag_summary}</td>
                </tr>
                """
        else:
            agent_rows_html = """
            <tr>
                <td colspan="3" style="padding: 12px; text-align: center; color: #64748b;">No agent execution activity logged.</td>
            </tr>
            """

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Analysis Report - {asset}</title>
    <style>
        @page {{
            size: letter;
            margin: 15mm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .brand {{
            font-size: 24px;
            font-weight: 800;
            color: #1e3a8a;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            font-size: 13px;
            color: #64748b;
            margin-top: 4px;
        }}
        .report-badge {{
            background: #eff6ff;
            color: #1d4ed8;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid #bfdbfe;
        }}
        .query-box {{
            background: #f8fafc;
            border-left: 4px solid #2563eb;
            padding: 14px 18px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 24px;
        }}
        .query-title {{
            font-size: 12px;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .query-text {{
            font-size: 16px;
            font-weight: 600;
            color: #0f172a;
            margin-top: 4px;
        }}
        .grid-cards {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }}
        .card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .card-label {{
            font-size: 12px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .card-value {{
            font-size: 22px;
            font-weight: 800;
            margin-top: 6px;
        }}
        .card-subtext {{
            font-size: 12px;
            color: #475569;
            margin-top: 4px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 12px;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 6px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 28px;
        }}
        th {{
            background-color: #f1f5f9;
            color: #475569;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-align: left;
            padding: 10px;
            border-bottom: 2px solid #cbd5e1;
        }}
        .disclaimer {{
            margin-top: 36px;
            padding: 16px;
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            font-size: 11px;
            color: #991b1b;
            line-height: 1.4;
        }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="brand">FINSIGHT 2.0</div>
            <div class="subtitle">SmartFinancial Advisor — Autonomous Multi-Agent Executive Report</div>
        </div>
        <div>
            <span class="report-badge">CONFIDENTIAL / EXECUTIVE</span>
            <div class="subtitle" style="text-align: right; margin-top: 6px;">Generated: {now_str}</div>
        </div>
    </div>

    <div class="query-box">
        <div class="query-title">Target Asset & Analysis Prompt</div>
        <div class="query-text">[{asset_type}] {asset} — "{query}"</div>
        <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Record Timestamp: {created_at}</div>
    </div>

    <div class="grid-cards">
        <div class="card">
            <div class="card-label">Recommendation</div>
            <div class="card-value" style="color: {rec_color};">{rec}</div>
            <div class="card-subtext">Score: {rec_score}/100</div>
        </div>
        <div class="card">
            <div class="card-label">Risk Profile</div>
            <div class="card-value" style="color: {risk_color};">{risk_level}</div>
            <div class="card-subtext">Score: {risk_score}/100</div>
        </div>
        <div class="card">
            <div class="card-label">Confidence & Sentiment</div>
            <div class="card-value" style="color: #2563eb;">{confidence}</div>
            <div class="card-subtext">Market: {market_dir} | News: {sentiment}</div>
        </div>
    </div>

    <div class="section-title">Multi-Agent Execution Breakdown</div>
    <table>
        <thead>
            <tr>
                <th style="width: 25%;">Agent Name</th>
                <th style="width: 20%;">Execution Status</th>
                <th style="width: 55%;">Execution Summary</th>
            </tr>
        </thead>
        <tbody>
            {agent_rows_html}
        </tbody>
    </table>

    <div class="disclaimer">
        <strong>IMPORTANT FINANCIAL DISCLAIMER:</strong> This report is produced by an automated algorithmic multi-agent artificial intelligence system for analytical and decision-support purposes only. It does not constitute formal financial, investment, legal, or tax advice. Market instruments involve substantial risk of potential monetary loss. Always perform independent due diligence before placing financial orders.
    </div>
</body>
</html>
"""
        return html_doc
