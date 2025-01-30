"""
Documentation action using Tavily search
"""
from typing import Optional, Any, Dict, Callable
from pydantic import BaseModel, ConfigDict
from cdp_agentkit_core.actions import CdpAction


class DocumentationSearchInput(BaseModel):
    """
    Input schema for documentation search
    """
    query: str
    max_results: Optional[int] = 3


async def search_documentation(query: str, max_results: int = 3) -> str:
    """
    Search for Base and CDP documentation using Tavily Search
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 3)
    
    Returns:
        str: A formatted string containing the search results
    """
    from core.services import tavily_web_search
    
    # Focus search on official documentation sources
    refined_query = f"{query} site:docs.cdp.coinbase.com OR site:docs.base.org"
    
    try:
        response = await tavily_web_search(
            query=refined_query,
            count=max_results
        )
        
        if not response or not response.get('webPages', {}).get('value'):
            return f"No documentation found for query: {query}"
        
        # Format results
        results = response['webPages']['value']
        formatted_results = "\n\nDocumentation Results:\n"
        
        for i, result in enumerate(results[:max_results], 1):
            formatted_results += f"\n{i}. {result['name']}\n"
            formatted_results += f"   URL: {result['url']}\n"
            formatted_results += f"   Summary: {result['snippet']}\n"
        
        return formatted_results
    
    except Exception as e:
        return f"Error searching documentation: {str(e)}"


class DocumentationSearchAction(CdpAction):
    """CDP Documentation Search Action"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "search_documentation"
    description: str = (
        "This tool searches official CDP and Base documentation for relevant information. "
        "Use this when you need to find specific protocol documentation, guides, or reference material."
    )
    args_schema: type[BaseModel] = DocumentationSearchInput
    func: Callable = search_documentation