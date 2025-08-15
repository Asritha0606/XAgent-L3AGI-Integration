"""
File 2: dialogue_agent_with_tools.py
Replacement for the original L3AGI dialogue agent
"""

from typing import List, Dict, Any, Optional
# from xagent_core import XAgentWrapper, XAgentTool
# The xagent_core package is not available on PyPI or cannot be installed.
# If you have the source code for XAgentWrapper and XAgentTool, place it in your project directory and import it directly.
# Otherwise, you need to obtain the correct package or module for these classes.

# Example fallback (replace with actual implementation or correct import):
# from xagent_core.xagent_wrapper import XAgentWrapper
# from xagent_core.xagent_tool import XAgentTool
# dialogue_agent_with_tools.py

from xagent_core import XAgentTool

# Import or define XAgentWrapper
try:
    from xagent_core import XAgentWrapper
except ImportError:
    # Minimal stub for XAgentWrapper if not defined in xagent_core
    class XAgentWrapper:
        def __init__(self, name, system_message, tools, model):
            self.name = name
            self.system_message = system_message
            self.tools = tools
            self.model = model

class DialogueAgentWithTools:
    def __init__(self, name, system_message, tools, model):
        self.name = name
        self.system_message = system_message
        self.tools = tools
        self.model = model
        self.agent = XAgentWrapper(
            name=name,
            system_message=system_message,
            tools=tools,
            model=model
        )

class DialogueAgentWithTools:
    """
    L3AGI DialogueAgentWithTools replacement using XAgent
    This maintains the same interface as the original Langchain version
    """
    
    def __init__(self, 
                 name: str, 
                 system_message: str, 
                 tools: List[Any], 
                 model: str = "gpt-3.5-turbo"):
        """
        Initialize dialogue agent with XAgent backend
        
        Args:
            name: Agent name
            system_message: System prompt for the agent
            tools: List of tools (Langchain format will be converted)
            model: LLM model to use
        """
        self.name = name
        self.system_message = system_message
        self.model = model
        
        # Initialize XAgent wrapper
        self.agent = XAgentWrapper(
            name=name,
            system_message=system_message,
            tools=tools,
            model=model
        )
    
    def send(self, message: str) -> Dict[str, Any]:
        """
        Send message to agent (maintains Langchain interface)
        
        Args:
            message: Input message
            
        Returns:
            Dict with agent response
        """
        try:
            response = self.agent.send(message)
            
            # Convert to expected L3AGI format
            return {
                "role": response.role,
                "content": response.content,
                "name": response.name,
                "timestamp": response.timestamp,
                "tool_calls": response.tool_calls,
                "reasoning": response.reasoning
            }
        except Exception as e:
            return {
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "name": self.name,
                "timestamp": None,
                "tool_calls": [],
                "reasoning": f"Error occurred: {str(e)}"
            }
    
    def reset(self):
        """Reset agent state"""
        self.agent.reset()
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.agent.get_conversation_history()

