"""
NewsData Financial News Data Service

This service module handles communication with the NewsData.io API to retrieve financial news articles.
It reads the API key securely from environment variables (.env) and formats response data into a clean structure.
"""

import os
from typing import Any, Dict, Optional
import httpx
from dotenv import load_dotenv

# Ensure environment variables from .env are loaded
load_dotenv()

NEWSDATA_BASE_URL = "https://newsdata.io/api/1/news"


class NewsDataService:
    """Service client for fetching financial news articles from NewsData.io API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NewsData Service.
        Reads API key from parameters or environment variable NEWSDATA_API_KEY.
        """
        self.api_key = api_key or os.getenv("NEWSDATA_API_KEY")

    def get_financial_news(
        self,
        query: str = "finance",
        category: Optional[str] = "business",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetch financial news articles matching a search query and optional category filter.

        :param query: Search term or keyword (defaults to 'finance').
        :param category: News category filter (defaults to 'business').
        :param language: Article language code (defaults to 'en').
        :return: Clean, structured dictionary containing list of formatted news articles or error details.
        """
        if not self.api_key or self.api_key.strip() in ("", "your_newsdata_api_key_here"):
            return {
                "success": False,
                "error": "Missing or unconfigured NewsData API key. Please set NEWSDATA_API_KEY in your .env file."
            }

        if not query or not query.strip():
            return {
                "success": False,
                "error": "Invalid search query provided."
            }

        clean_query = query.strip()
        params: Dict[str, Any] = {
            "apikey": self.api_key,
            "q": clean_query,
            "language": language
        }

        if category and category.strip():
            params["category"] = category.strip()

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(NEWSDATA_BASE_URL, params=params)

                if response.status_code == 429:
                    return {
                        "success": False,
                        "error": "NewsData API Rate Limit Exceeded (HTTP 429). Please try again later."
                    }

                response.raise_for_status()
                data = response.json()

            # Handle NewsData API error response payload
            if data.get("status") == "error":
                results = data.get("results", {})
                error_msg = results.get("message") if isinstance(results, dict) else str(results)
                return {
                    "success": False,
                    "error": f"NewsData API Error: {error_msg or 'Unknown API error'}"
                }

            results_list = data.get("results", [])
            if not isinstance(results_list, list) or len(results_list) == 0:
                return {
                    "success": False,
                    "error": f"No news articles found for query '{clean_query}'."
                }

            # Format article data into a clean structure
            articles = []
            for item in results_list:
                if not isinstance(item, dict):
                    continue

                source_info = item.get("source_id") or item.get("source_url") or "Unknown Source"

                articles.append({
                    "article_id": str(item.get("article_id", "")),
                    "title": item.get("title", "No Title"),
                    "link": item.get("link", ""),
                    "description": item.get("description", "") or "",
                    "pubDate": item.get("pubDate", ""),
                    "source": str(source_info)
                })

            return {
                "success": True,
                "total_results": len(articles),
                "data": articles
            }

        except httpx.HTTPStatusError as err:
            return {
                "success": False,
                "error": f"HTTP Error {err.response.status_code}: {err.response.text}"
            }
        except httpx.RequestError as err:
            return {
                "success": False,
                "error": f"Network error connecting to NewsData: {str(err)}"
            }
        except (ValueError, KeyError, TypeError) as err:
            return {
                "success": False,
                "error": f"Unexpected response format from NewsData: {str(err)}"
            }
