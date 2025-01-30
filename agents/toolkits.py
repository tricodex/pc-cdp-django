"""
Custom toolkits for the framework
"""
from typing import List
from pydantic import BaseModel, ConfigDict
from langchain_core.tools import BaseTool
from langchain_core.tools.base import BaseToolkit
from cdp_langchain.tools import CdpTool
from cdp_langchain.utils import CdpAgentkitWrapper
from agents.actions import ALL_ACTIONS


class CustomAgentToolkit(BaseToolkit, BaseModel):
    """Extended toolkit including custom actions"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _tools: List[BaseTool] = []

    @classmethod
    def from_cdp_agentkit_wrapper(cls, cdp_agentkit_wrapper: CdpAgentkitWrapper) -> "CustomAgentToolkit":
        """Create toolkit from CDP wrapper with all actions"""
        toolkit = cls()
        toolkit._tools = []
        
        for action in ALL_ACTIONS:
            tool = CdpTool(
                name=action.name,
                description=action.description,
                cdp_agentkit_wrapper=cdp_agentkit_wrapper,
                func=action.func,
                args_schema=action.args_schema
            )
            toolkit._tools.append(tool)
        
        return toolkit

    def get_tools(self) -> List[BaseTool]:
        """Get all tools"""
        return self._tools