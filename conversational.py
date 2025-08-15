"""
File 3: conversational.py
Conversation management with XAgent integration
"""

import json
from typing import List, Dict, Any
from datetime import datetime
# Ensure 'dialogue_agent_with_tools.py' is in the same directory or update the import path accordingly.
# Make sure 'dialogue_agent_with_tools.py' is present in the same directory as this file.
# If you see "Import 'dialogue_agent_with_tools' could not be resolved",
# manually place 'dialogue_agent_with_tools.py' in your project folder.
# Example:
# - conversational.py
# - dialogue_agent_with_tools.py
# Then the import will work as a local module.
import sys
import os
dialogue_agent_path = r"C:\Users\asrit\OneDrive\ドキュメント\Pyt"
if dialogue_agent_path not in sys.path:
    sys.path.append(dialogue_agent_path)
try:
    from dialogue_agent_with_tools import DialogueAgentWithTools
except ModuleNotFoundError:
    raise ImportError(
        "Could not import 'dialogue_agent_with_tools'. "
        "Make sure 'dialogue_agent_with_tools.py' is in the directory: C:\\Users\\asrit\\OneDrive\\ドキュメント\\Pyt"
    )

class ConversationManager:
    """
    Manages conversations between multiple XAgent-powered agents.
    """

    def __init__(self, agents: List[DialogueAgentWithTools]):
        """
        Initialize conversation manager

        Args:
            agents: List of DialogueAgentWithTools instances
        """
        self.agents = {agent.name: agent for agent in agents}
        self.conversation_log = []
        self.current_speaker = None
        self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def step(self, agent_name: str, message: str) -> Dict[str, Any]:
        """
        Execute one conversation step

        Args:
            agent_name: Name of the agent to respond
            message: Input message

        Returns:
            Agent response dictionary
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}")

        agent = self.agents[agent_name]
        self.current_speaker = agent_name

        try:
            # Get response from agent
            response = agent.send(message)

            # Log the conversation step
            step_log = {
                "step_id": len(self.conversation_log) + 1,
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "input_message": message,
                "response": response,
                "conversation_id": self.conversation_id
            }

            self.conversation_log.append(step_log)

            return response

        except Exception as e:
            error_response = {
                "role": "assistant",
                "content": f"Error in agent {agent_name}: {str(e)}",
                "name": agent_name,
                "timestamp": datetime.now().isoformat(),
                "tool_calls": [],
                "reasoning": f"Error occurred: {str(e)}"
            }

            step_log = {
                "step_id": len(self.conversation_log) + 1,
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "input_message": message,
                "response": error_response,
                "error": True,
                "conversation_id": self.conversation_id
            }

            self.conversation_log.append(step_log)
            return error_response

    def multi_agent_conversation(self, 
                                 participants: List[str], 
                                 initial_message: str,
                                 max_turns: int = 5) -> List[Dict]:
        """
        Run a multi-agent conversation

        Args:
            participants: List of agent names to participate
            initial_message: Starting message
            max_turns: Maximum number of conversation turns

        Returns:
            List of conversation responses
        """
        if not all(agent in self.agents for agent in participants):
            missing = [agent for agent in participants if agent not in self.agents]
            raise ValueError(f"Agents not found: {missing}")

        conversation_responses = []
        current_message = initial_message

        for turn in range(max_turns):
            for participant in participants:
                try:
                    # Add context about the conversation
                    context_message = f"Turn {turn + 1}: {current_message}"
                    if turn > 0:
                        context_message += f"\nPrevious responses: {json.dumps(conversation_responses[-len(participants):], indent=2)}"

                    response = self.step(participant, context_message)
                    conversation_responses.append({
                        "turn": turn + 1,
                        "participant": participant,
                        "response": response
                    })

                    # Use this response as input for next agent
                    current_message = response.get("content", "")

                except Exception as e:
                    error_response = {
                        "turn": turn + 1,
                        "participant": participant,
                        "response": {
                            "role": "assistant",
                            "content": f"Error: {str(e)}",
                            "name": participant,
                            "error": True
                        }
                    }
                    conversation_responses.append(error_response)

        return conversation_responses

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get summary of current conversation

        Returns:
            Conversation summary dictionary
        """
        return {
            "conversation_id": self.conversation_id,
            "total_steps": len(self.conversation_log),
            "participants": list(self.agents.keys()),
            "current_speaker": self.current_speaker,
            "start_time": self.conversation_log[0]["timestamp"] if self.conversation_log else None,
            "last_activity": self.conversation_log[-1]["timestamp"] if self.conversation_log else None,
            "recent_steps": self.conversation_log[-5:] if len(self.conversation_log) > 5 else self.conversation_log
        }

    def export_conversation(self, filename: str = None) -> str:
        """
        Export conversation to JSON file

        Args:
            filename: Output filename (optional)

        Returns:
            Filename of exported conversation
        """
        if filename is None:
            filename = f"conversation_{self.conversation_id}.json"

        export_data = {
            "conversation_summary": self.get_conversation_summary(),
            "conversation_log": self.conversation_log,
            "agents": {name: {"name": agent.name, "model": agent.model} 
                      for name, agent in self.agents.items()}
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            raise Exception(f"Failed to export conversation: {str(e)}")

    def reset_all_agents(self):
        """Reset all agents in the conversation"""
        for agent in self.agents.values():
            agent.reset()
        self.conversation_log = []
        self.current_speaker = None

