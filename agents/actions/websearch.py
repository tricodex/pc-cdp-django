"""
Web search action using Tavily search
"""
from typing import Optional, Any, Dict, Callable
from pydantic import BaseModel, ConfigDict
from cdp_agentkit_core.actions import CdpAction
import asyncio


class WebSearchInput(BaseModel):
    """Input schema for web search"""
    query: str
    max_results: Optional[int] = 3


async def _search_web(parameters: Dict[str, Any], **kwargs) -> str:
    """
    Search the web using Tavily Search
    
    Args:
        parameters: Dictionary containing search parameters
        kwargs: Additional keyword arguments
    
    Returns:
        str: A formatted string containing the search results
    """
    from core.services import tavily_web_search
    
    query = parameters.get('query', '')
    max_results = parameters.get('max_results', 3)
    
    try:
        response = await tavily_web_search(
            query=query,
            count=max_results
        )
        
        if not response or not response.get('webPages', {}).get('value'):
            return f"No results found for query: {query}"
        
        # Format results
        results = response['webPages']['value']
        formatted_results = "\n\nWeb Search Results:\n"
        
        for i, result in enumerate(results[:max_results], 1):
            formatted_results += f"\n{i}. {result['name']}\n"
            formatted_results += f"   URL: {result['url']}\n"
            formatted_results += f"   Summary: {result['snippet']}\n"
        
        return formatted_results
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def search_web(parameters: Dict[str, Any] = None, **kwargs) -> str:
    """Synchronous wrapper for web search"""
    if parameters is None:
        parameters = {}
        
    # Extract query from kwargs if not in parameters
    if 'query' not in parameters and kwargs.get('query'):
        parameters['query'] = kwargs['query']
    
    # Ensure required parameters are present
    if 'query' not in parameters:
        return "Error: No search query provided. Please provide a query to search for."
        
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(_search_web(parameters, **kwargs))
    finally:
        if not loop.is_closed():
            loop.close()


class WebSearchAction(CdpAction):
    """General Web Search Action"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "search_web"
    description: str = (
        "This tool performs web searches to find information. To use it, provide a 'query' parameter with your search term. "
        "For example: { \"query\": \"what is deepseek v3\" }. "
        "The tool will return search results with titles, URLs, and summaries."
    )
    args_schema: type[BaseModel] = WebSearchInput
    func: Callable = search_web
