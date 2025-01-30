"""
Core services for the framework
"""
from typing import Dict, Any
from tavily import TavilyClient
from django.conf import settings


async def tavily_web_search(query: str, count: int = 5) -> Dict[str, Any]:
    """
    Perform a web search using Tavily's API.
    
    Args:
        query: Search query
        count: Number of results to return
        
    Returns:
        dict: Search results containing webpage data formatted like Brave Search API
    """
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    try:
        response = client.search(query, search_depth="basic", max_results=min(count, 10))
        
        # Transform Tavily response to match Brave Search format
        results = [
            {
                'name': result.get('title', ''),
                'url': result.get('url', ''),
                'snippet': result.get('content', '')
            }
            for result in response.get('results', [])
        ]
        
        return {
            'webPages': {
                'value': results
            }
        }
        
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")