"""
File 4: test.py
Comprehensive testing suite for XAgent integration
"""

import unittest
import sys
import os
from typing import List, Dict, Any
import sys
sys.path.append(r"C:\Users\asrit\OneDrive\ドキュメント\Pyt")

from dialogue_agent_with_tools import DialogueAgentWithTools
from conversational import ConversationManager
from xagent_core import XAgentTool
import io
   

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Sample tools for testing
def sample_search_tool(query: str) -> str:
    """Sample search tool for testing"""
    return f"Search results for: {query}"

def sample_calculator_tool(expression: str) -> str:
    """Sample calculator tool for testing"""
    try:
        result = eval(expression)
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

def sample_weather_tool(location: str) -> str:
    """Sample weather tool for testing"""
    return f"Weather in {location}: Sunny, 22°C"

class TestXAgentIntegration(unittest.TestCase):
    """Test suite for XAgent L3AGI integration"""
    
    def setUp(self):
        """Set up test environment"""
        # Create sample tools
        self.tools = [
            type('Tool', (), {
                'name': 'search',
                'description': 'Search for information',
                'func': sample_search_tool
            })(),
            type('Tool', (), {
                'name': 'calculator',
                'description': 'Perform calculations',
                'func': sample_calculator_tool
            })(),
            type('Tool', (), {
                'name': 'weather',
                'description': 'Get weather information',
                'func': sample_weather_tool
            })()
        ]
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = DialogueAgentWithTools(
            name="TestAgent",
            system_message="You are a helpful assistant.",
            tools=self.tools,
            model="gpt-3.5-turbo"
        )
        
        self.assertEqual(agent.name, "TestAgent")
        self.assertIsNotNone(agent.agent)
        print("✅ Agent initialization test passed")
    
    def test_basic_conversation(self):
        """Test basic conversation functionality"""
        agent = DialogueAgentWithTools(
            name="TestAgent",
            system_message="You are a helpful assistant.",
            tools=[],
            model="gpt-3.5-turbo"
        )
        
        response = agent.send("Hello, how are you?")
        
        self.assertIsInstance(response, dict)
        self.assertIn("content", response)
        self.assertIn("role", response)
        self.assertEqual(response["role"], "assistant")
        print(f"✅ Basic conversation test passed: {response['content'][:50]}...")
    
    def test_tool_integration(self):
        """Test tool integration and usage"""
        agent = DialogueAgentWithTools(
            name="ToolAgent",
            system_message="You are an assistant with access to tools.",
            tools=self.tools,
            model="gpt-3.5-turbo"
        )
        
        response = agent.send("Search for Python programming tutorials")
        
        self.assertIsInstance(response, dict)
        self.assertIn("content", response)
        print(f"✅ Tool integration test passed: {response['content'][:50]}...")
    
    def test_conversation_manager(self):
        """Test conversation manager functionality"""
        # Create multiple agents
        agent1 = DialogueAgentWithTools(
            name="Researcher",
            system_message="You are a research specialist.",
            tools=self.tools,
            model="gpt-3.5-turbo"
        )
        
        agent2 = DialogueAgentWithTools(
            name="Analyst",
            system_message="You are a data analyst.",
            tools=self.tools,
            model="gpt-3.5-turbo"
        )
        
        # Create conversation manager
        conversation = ConversationManager([agent1, agent2])
        
        # Test conversation step
        response1 = conversation.step("Researcher", "Research AI trends")
        response2 = conversation.step("Analyst", "Analyze the research findings")
        
        self.assertIsInstance(response1, dict)
        self.assertIsInstance(response2, dict)
        
        # Test conversation summary
        summary = conversation.get_conversation_summary()
        self.assertEqual(summary["total_steps"], 2)
        
        print("✅ Conversation manager test passed")
    
    def test_multi_agent_conversation(self):
        """Test multi-agent conversation"""
        agents = [
            DialogueAgentWithTools(
                name="Agent1",
                system_message="You are agent 1.",
                tools=[],
                model="gpt-3.5-turbo"
            ),
            DialogueAgentWithTools(
                name="Agent2",
                system_message="You are agent 2.",
                tools=[],
                model="gpt-3.5-turbo"
            )
        ]
        
        conversation = ConversationManager(agents)
        responses = conversation.multi_agent_conversation(
            participants=["Agent1", "Agent2"],
            initial_message="Let's discuss AI ethics",
            max_turns=2
        )
        
        self.assertEqual(len(responses), 4)  # 2 agents × 2 turns
        print("✅ Multi-agent conversation test passed")
    
    def test_error_handling(self):
        """Test error handling"""
        agent = DialogueAgentWithTools(
            name="ErrorTestAgent",
            system_message="Test agent for errors.",
            tools=[],
            model="invalid-model"  # This should trigger fallback behavior
        )
        
        response = agent.send("Test message")
        
        # Should still return a response even with invalid model
        self.assertIsInstance(response, dict)
        self.assertIn("content", response)
        print("✅ Error handling test passed")
    
    def test_conversation_export(self):
        """Test conversation export functionality"""
        agent = DialogueAgentWithTools(
            name="ExportTestAgent",
            system_message="Test agent for export.",
            tools=[],
            model="gpt-3.5-turbo"
        )
        
        conversation = ConversationManager([agent])
        conversation.step("ExportTestAgent", "Hello")
        
        filename = conversation.export_conversation("test_conversation.json")
        
        # Check if file was created
        self.assertTrue(os.path.exists(filename))
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        print("✅ Conversation export test passed")

def run_integration_demo():
    """
    Run a complete integration demonstration
    """
    print("\n" + "="*50)
    print("XAgent L3AGI Integration Demonstration")
    print("="*50)
    
    # Create tools
    tools = [
        type('Tool', (), {
            'name': 'search',
            'description': 'Search for information on any topic',
            'func': lambda query: f"Found information about: {query}"
        })(),
        type('Tool', (), {
            'name': 'analyze',
            'description': 'Analyze data or information',
            'func': lambda data: f"Analysis of {data}: This appears to be relevant information."
        })()
    ]
    
    # Create agents
    researcher = DialogueAgentWithTools(
        name="Researcher",
        system_message="You are an AI research specialist. You help find and organize information.",
        tools=tools,
        model="gpt-3.5-turbo"
    )
    
    analyst = DialogueAgentWithTools(
        name="Analyst",
        system_message="You are a data analyst. You help interpret and analyze information.",
        tools=tools,
        model="gpt-3.5-turbo"
    )
    
    # Single agent demo
    print("\n1. Single Agent Demo:")
    print("-" * 20)
    response = researcher.send("Can you search for information about machine learning trends?")
    print(f"Researcher: {response['content']}")
    
    # Multi-agent demo
    print("\n2. Multi-Agent Conversation Demo:")
    print("-" * 30)
    
    conversation = ConversationManager([researcher, analyst])
    
    # Step 1: Researcher finds information
    response1 = conversation.step("Researcher", "Research the latest developments in AI and machine learning")
    print(f"Step 1 - Researcher: {response1['content']}")
    
    # Step 2: Analyst analyzes the findings
    response2 = conversation.step("Analyst", f"Please analyze this research: {response1['content']}")
    print(f"Step 2 - Analyst: {response2['content']}")
    
    # Conversation summary
    print("\n3. Conversation Summary:")
    print("-" * 25)
    summary = conversation.get_conversation_summary()
    print(f"Total steps: {summary['total_steps']}")
    print(f"Participants: {', '.join(summary['participants'])}")
    
    print("\n✅ Integration demonstration completed successfully!")

if __name__ == "__main__":
    # Run tests
    print("Running XAgent L3AGI Integration Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run demonstration
    run_integration_demo()
