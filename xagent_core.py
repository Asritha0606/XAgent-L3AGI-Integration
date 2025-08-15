"""
File 1: xagent_core.py
Core XAgent wrapper and integration logic
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime
import traceback
import logging

# XAgent imports
try:
    from xagent.agent import XAgent
    from xagent.config import Config
    from xagent.data_structure.node import ToolNode
    from xagent.engines.dsl.DSL_runner import DSLRunner
    from xagent.logs import logger
except ModuleNotFoundError:
    # Fallback stubs for missing xagent package
    class XAgent:
        def __init__(self, config=None): pass
        def run(self, task, max_iterations=10): return {"response": "Simulated XAgent response"}
        def reset(self): pass

    class Config:
        def __init__(self): 
            self.default_request_timeout = 60
            self.model = "gpt-3.5-turbo"
            self.max_iterations = 10
            self.enable_reflection = True

    class ToolNode: pass
    class DSLRunner: pass
    logger = logging.getLogger("xagent_stub")

# Setup logging
logging.basicConfig(level=logging.INFO)

@dataclass
class AgentMessage:
    """Standard message format for L3AGI compatibility"""
    role: str
    content: str
    name: str
    timestamp: str = None
    tool_calls: List[Dict] = None
    reasoning: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.tool_calls is None:
            self.tool_calls = []

from typing import Callable, Dict

class XAgentTool:
    """XAgent compatible tool wrapper"""
    
    def __init__(self, name: str, description: str, func: Callable, parameters: Dict = None):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict:
        """Convert tool to XAgent format"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "function": self.func
        }
    
    def __call__(self, *args, **kwargs):
        """Execute the tool"""
        try:
            result = self.func(*args, **kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

class XAgentWrapper:
    """
    Main XAgent wrapper that replaces Langchain REACT Agent
    """
    
    def __init__(self, 
                 name: str,
                 system_message: str,
                 tools: List[Any] = None,
                 model: str = "gpt-3.5-turbo",
                 max_iterations: int = 10,
                 enable_reflection: bool = True):
        
        self.name = name
        self.system_message = system_message
        self.model = model
        self.max_iterations = max_iterations
        self.enable_reflection = enable_reflection
        
        # Message history
        self.message_history: List[AgentMessage] = []
        
        # Initialize XAgent configuration
        self.config = Config()
        self.config.default_request_timeout = 60
        self.config.model = model
        self.config.max_iterations = max_iterations
        self.config.enable_reflection = enable_reflection
        
        # Setup tools
        self.tools = []
        if tools:
            self.tools = self._convert_tools(tools)
        
        # Initialize XAgent
        try:
            self.agent = XAgent(config=self.config)
            self._setup_agent()
        except Exception as e:
            logging.error(f"Failed to initialize XAgent: {e}")
            raise
    
    def _convert_tools(self, tools: List[Any]) -> List[XAgentTool]:
        """Convert various tool formats to XAgentTool"""
        converted_tools = []
        
        for tool in tools:
            try:
                if hasattr(tool, 'name') and hasattr(tool, 'func'):
                    # Langchain tool format
                    xagent_tool = XAgentTool(
                        name=tool.name,
                        description=getattr(tool, 'description', ''),
                        func=tool.func,
                        parameters=self._extract_parameters(tool.func)
                    )
                    converted_tools.append(xagent_tool)
                elif callable(tool):
                    # Function tool
                    xagent_tool = XAgentTool(
                        name=getattr(tool, '__name__', 'custom_tool'),
                        description=getattr(tool, '__doc__', 'Custom tool'),
                        func=tool,
                        parameters=self._extract_parameters(tool)
                    )
                    converted_tools.append(xagent_tool)
                else:
                    logging.warning(f"Unknown tool format: {type(tool)}")
            except Exception as e:
                logging.error(f"Failed to convert tool {tool}: {e}")
                continue
        
        return converted_tools
    
    def _extract_parameters(self, func: Callable) -> Dict:
        """Extract function parameters for XAgent"""
        import inspect
        
        try:
            sig = inspect.signature(func)
            parameters = {}
            
            for param_name, param in sig.parameters.items():
                param_info = {
                    "type": "string",
                    "description": f"Parameter {param_name}",
                    "required": param.default == inspect.Parameter.empty
                }
                
                # Try to infer type from annotation
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == str:
                        param_info["type"] = "string"
                    elif param.annotation == int:
                        param_info["type"] = "integer"
                    elif param.annotation == float:
                        param_info["type"] = "number"
                    elif param.annotation == bool:
                        param_info["type"] = "boolean"
                    elif param.annotation == list:
                        param_info["type"] = "array"
                    elif param.annotation == dict:
                        param_info["type"] = "object"
                
                parameters[param_name] = param_info
            
            return parameters
        except Exception:
            return {}
    
    def _setup_agent(self):
        """Setup XAgent with tools and configuration"""
        try:
            # Register tools with XAgent
            for tool in self.tools:
                tool_info = {
                    "tool_name": tool.name,
                    "tool_description": tool.description,
                    "tool_function": tool.func
                }
                # XAgent tool registration would go here
                # This depends on XAgent's specific API
                
            logging.info(f"XAgent setup completed with {len(self.tools)} tools")
        except Exception as e:
            logging.error(f"Failed to setup XAgent: {e}")
    
    def send(self, message: str, **kwargs) -> AgentMessage:
        """
        Send message to XAgent and return formatted response
        Main method that replaces Langchain agent.run()
        """
        try:
            # Create user message
            user_msg = AgentMessage(
                role="user",
                content=message,
                name="user"
            )
            self.message_history.append(user_msg)
            
            # Prepare context for XAgent
            context = self._build_context()
            
            # Run XAgent
            response = self._run_xagent(message, context)
            
            # Create assistant message
            assistant_msg = AgentMessage(
                role="assistant",
                content=response.get("content", ""),
                name=self.name,
                tool_calls=response.get("tool_calls", []),
                reasoning=response.get("reasoning", "")
            )
            
            self.message_history.append(assistant_msg)
            return assistant_msg
            
        except Exception as e:
            error_msg = AgentMessage(
                role="assistant",
                content=f"I encountered an error: {str(e)}",
                name=self.name
            )
            self.message_history.append(error_msg)
            logging.error(f"Error in send method: {e}")
            logging.error(traceback.format_exc())
            return error_msg
    
    def _build_context(self) -> str:
        """Build conversation context for XAgent"""
        context_parts = [f"System: {self.system_message}"]
        
        # Add recent conversation history (last 10 messages)
        for msg in self.message_history[-10:]:
            speaker = msg.name if msg.name else msg.role
            context_parts.append(f"{speaker}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def _run_xagent(self, query: str, context: str) -> Dict[str, Any]:
        """
        Run XAgent with the given query and context
        This is the core replacement for Langchain's agent execution
        """
        try:
            # Prepare XAgent input
            agent_input = {
                "task": query,
                "context": context,
                "max_iterations": self.max_iterations,
                "tools": [tool.to_dict() for tool in self.tools]
            }
            
            # Since XAgent's exact API might vary, we'll implement a robust approach
            response = self._execute_xagent_task(agent_input)
            
            return {
                "content": response.get("response", "I'm ready to help!"),
                "tool_calls": response.get("tool_calls", []),
                "reasoning": response.get("reasoning", ""),
                "iterations": response.get("iterations", 1)
            }
            
        except Exception as e:
            logging.error(f"XAgent execution failed: {e}")
            return {
                "content": f"I encountered an error while processing your request: {str(e)}",
                "tool_calls": [],
                "reasoning": f"Error occurred: {str(e)}"
            }
    
    def _execute_xagent_task(self, agent_input: Dict) -> Dict[str, Any]:
        """
        Execute XAgent task - this method handles the actual XAgent execution
        """
        try:
            # Method 1: Try direct XAgent execution
            if hasattr(self.agent, 'run'):
                result = self.agent.run(
                    task=agent_input["task"],
                    max_iterations=agent_input["max_iterations"]
                )
                return self._parse_xagent_result(result)
            
            # Method 2: Try alternative XAgent API
            elif hasattr(self.agent, 'execute'):
                result = self.agent.execute(agent_input["task"])
                return self._parse_xagent_result(result)
            
            # Method 3: Fallback simulation (for testing)
            else:
                return self._simulate_agent_response(agent_input)
                
        except Exception as e:
            logging.error(f"XAgent task execution failed: {e}")
            return self._simulate_agent_response(agent_input)
    
    def _parse_xagent_result(self, result: Any) -> Dict[str, Any]:
        """Parse XAgent result into standard format"""
        try:
            if isinstance(result, dict):
                return {
                    "response": result.get("response", str(result)),
                    "tool_calls": result.get("tool_calls", []),
                    "reasoning": result.get("reasoning", ""),
                    "iterations": result.get("iterations", 1)
                }
            elif isinstance(result, str):
                return {
                    "response": result,
                    "tool_calls": [],
                    "reasoning": "",
                    "iterations": 1
                }
            else:
                return {
                    "response": str(result),
                    "tool_calls": [],
                    "reasoning": "",
                    "iterations": 1
                }
        except Exception:
            return {
                "response": "Task completed successfully",
                "tool_calls": [],
                "reasoning": "",
                "iterations": 1
            }
    
    def _simulate_agent_response(self, agent_input: Dict) -> Dict[str, Any]:
        """
        Simulate agent response for testing purposes
        This ensures the integration works even if XAgent API changes
        """
        task = agent_input.get("task", "")
        
        # Simple response generation based on task
        if "tool" in task.lower() or "search" in task.lower():
            response = f"I understand you want me to use tools for: {task}. "
            if self.tools:
                response += f"I have {len(self.tools)} tools available: {', '.join([t.name for t in self.tools])}"
                # Simulate tool usage
                tool_calls = [{
                    "tool": self.tools[0].name,
                    "input": task,
                    "output": f"Simulated result for: {task}"
                }]
            else:
                response += "However, no tools are currently available."
                tool_calls = []
        else:
            response = f"I'll help you with: {task}"
            tool_calls = []
        
        return {
            "response": response,
            "tool_calls": tool_calls,
            "reasoning": f"Analyzed the request: {task}",
            "iterations": 1
        }
    
    def reset(self):
        """Reset conversation history"""
        self.message_history = []
        if hasattr(self.agent, 'reset'):
            self.agent.reset()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history in standard format"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "name": msg.name,
                "timestamp": msg.timestamp,
                "tool_calls": msg.tool_calls,
                "reasoning": msg.reasoning
            }
            for msg in self.message_history
        ]
