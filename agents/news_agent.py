"""
Financial News Agent Module

This module implements the NewsAgent, which uses the NewsDataService to retrieve
financial news articles, performs deterministic sentiment analysis, and returns a structured output.
"""

from typing import Any, Dict, List, Optional, Set
from services.newsdata import NewsDataService

# Deterministic financial sentiment lexicons
POSITIVE_KEYWORDS: Set[str] = {
    "growth", "profit", "bullish", "rally", "gain", "surge",
    "rise", "high", "success", "record", "optimism", "upgrade"
}

NEGATIVE_KEYWORDS: Set[str] = {
    "loss", "bearish", "drop", "fall", "crash", "decline",
    "plunge", "risk", "warning", "inflation", "recession", "downgrade", "crisis"
}


class NewsAgent:
    """Autonomous agent for inspecting financial news and generating sentiment analysis."""

    def __init__(self, service: Optional[NewsDataService] = None):
        """
        Initialize the NewsAgent.
        Supports dependency injection of a custom or mock NewsDataService.
        """
        self.service = service or NewsDataService()

    def _analyze_article_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze article text for positive and negative financial keyword matches.

        :param text: Lowercased title and description text.
        :return: Dictionary containing positive count, negative count, and assigned sentiment.
        """
        words = set(text.lower().split())

        pos_matches = sum(1 for kw in POSITIVE_KEYWORDS if kw in text.lower())
        neg_matches = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text.lower())

        if pos_matches > neg_matches:
            sentiment = "positive"
        elif neg_matches > pos_matches:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "pos_count": pos_matches,
            "neg_count": neg_matches,
            "sentiment": sentiment
        }

    def analyze_news(
        self,
        query: str = "finance",
        category: Optional[str] = "business",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze financial news for a search query by fetching articles and scoring sentiment.

        :param query: Search query term (defaults to 'finance').
        :param category: News category (defaults to 'business').
        :param language: Language code (defaults to 'en').
        :return: Structured dictionary containing news sentiment results or error details.
        """
        if not query or not isinstance(query, str) or not query.strip():
            return {
                "success": False,
                "agent": "NewsAgent",
                "query": str(query) if query is not None else "",
                "error": "Invalid search query provided. Must be a non-empty string."
            }

        clean_query = query.strip()
        clean_category = category.strip() if category and category.strip() else "business"
        clean_language = language.strip() if language and language.strip() else "en"

        # Retrieve news articles using the service layer
        service_response = self.service.get_financial_news(
            query=clean_query,
            category=clean_category,
            language=clean_language
        )

        if not service_response.get("success"):
            return {
                "success": False,
                "agent": "NewsAgent",
                "query": clean_query,
                "error": service_response.get("error", "Failed to retrieve financial news data.")
            }

        articles_list = service_response.get("data", [])
        if not isinstance(articles_list, list) or len(articles_list) == 0:
            return {
                "success": False,
                "agent": "NewsAgent",
                "query": clean_query,
                "error": f"No news articles found for query '{clean_query}'."
            }

        analyzed_articles: List[Dict[str, Any]] = []
        total_pos_signals = 0
        total_neg_signals = 0

        for article in articles_list:
            if not isinstance(article, dict):
                continue

            title = article.get("title", "No Title")
            description = article.get("description", "")
            combined_text = f"{title} {description}"

            analysis_result = self._analyze_article_text(combined_text)
            total_pos_signals += analysis_result["pos_count"]
            total_neg_signals += analysis_result["neg_count"]

            analyzed_articles.append({
                "article_id": str(article.get("article_id", "")),
                "title": title,
                "description": description,
                "link": str(article.get("link", "")),
                "published_at": str(article.get("pubDate", "")),
                "source": str(article.get("source", "Unknown Source")),
                "sentiment": analysis_result["sentiment"]
            })

        # Evaluate overall aggregate sentiment
        if total_pos_signals > total_neg_signals:
            overall_sentiment = "positive"
        elif total_neg_signals > total_pos_signals:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        summary_text = (
            f"Analyzed {len(analyzed_articles)} articles for '{clean_query}': "
            f"Overall sentiment is {overall_sentiment} ({total_pos_signals} positive signals, {total_neg_signals} negative signals)."
        )

        return {
            "success": True,
            "agent": "NewsAgent",
            "query": clean_query,
            "category": clean_category,
            "language": clean_language,
            "total_results": len(analyzed_articles),
            "overall_sentiment": overall_sentiment,
            "summary": summary_text,
            "articles": analyzed_articles
        }
