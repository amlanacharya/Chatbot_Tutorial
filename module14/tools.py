"""
Tools module for the agent framework.

This module provides a collection of tools that can be used by the agent to interact
with external systems and perform specific tasks.
"""

import json
import math
import datetime
import requests
from typing import Dict, Any, List, Callable, Optional

class ToolRegistry:
    """A registry for tools that can be used by the agent."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, name: str, description: str, function: Callable, 
                      parameters: Optional[List[Dict[str, Any]]] = None):
        """
        Register a new tool with the registry.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            function: The function to call when the tool is used
            parameters: Optional list of parameter descriptions
        """
        self.tools[name] = {
            "description": description,
            "function": function,
            "parameters": parameters or []
        }
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get a tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self.tools[name]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get a list of all available tools with their descriptions."""
        return [
            {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for name, tool in self.tools.items()
        ]
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name with the given parameters.
        
        Args:
            name: The name of the tool to execute
            **kwargs: Parameters to pass to the tool function
            
        Returns:
            The result of the tool execution
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        try:
            result = self.tools[name]["function"](**kwargs)
            return result
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"


# Define some example tools

def calculator(expression: str) -> float:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: A string containing a mathematical expression
        
    Returns:
        The result of evaluating the expression
    """
    # Replace common math functions with their math module equivalents
    expression = expression.replace("^", "**")
    
    # Create a safe local environment with only math functions
    safe_locals = {
        "abs": abs,
        "round": round,
        "max": max,
        "min": min,
        "sum": sum,
        "sqrt": math.sqrt,
        "pow": math.pow,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e
    }
    
    try:
        # Evaluate the expression in the safe environment
        result = eval(expression, {"__builtins__": {}}, safe_locals)
        return result
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")


def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time in the specified timezone.
    
    Args:
        timezone: The timezone to get the time for (default: UTC)
        
    Returns:
        The current time as a string
    """
    # For simplicity, we're just returning the current UTC time
    # In a real implementation, you would use pytz or similar to handle timezones
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Current time ({timezone}): {current_time}"


def search_wikipedia(query: str, limit: int = 1) -> str:
    """
    Search Wikipedia for information about a topic.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        A summary of the search results
    """
    # This is a simplified mock implementation
    # In a real implementation, you would use the Wikipedia API
    return f"Here's what I found about '{query}' on Wikipedia: " + \
           f"This is a mock implementation. In a real agent, this would " + \
           f"connect to the Wikipedia API and return actual search results."


def create_default_tool_registry() -> ToolRegistry:
    """Create and return a registry with default tools."""
    registry = ToolRegistry()
    
    # Register the calculator tool
    registry.register_tool(
        name="calculator",
        description="Perform mathematical calculations",
        function=calculator,
        parameters=[
            {
                "name": "expression",
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        ]
    )
    
    # Register the current time tool
    registry.register_tool(
        name="get_current_time",
        description="Get the current time in a specified timezone",
        function=get_current_time,
        parameters=[
            {
                "name": "timezone",
                "type": "string",
                "description": "The timezone to get the time for (default: UTC)"
            }
        ]
    )
    
    # Register the Wikipedia search tool
    registry.register_tool(
        name="search_wikipedia",
        description="Search Wikipedia for information about a topic",
        function=search_wikipedia,
        parameters=[
            {
                "name": "query",
                "type": "string",
                "description": "The search query"
            },
            {
                "name": "limit",
                "type": "integer",
                "description": "Maximum number of results to return (default: 1)"
            }
        ]
    )
    
    return registry


if __name__ == "__main__":
    # Test the tools
    registry = create_default_tool_registry()
    
    print("Available tools:")
    for tool in registry.list_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\nTesting calculator tool:")
    result = registry.execute_tool("calculator", expression="2 + 2 * 3")
    print(f"2 + 2 * 3 = {result}")
    
    print("\nTesting current time tool:")
    result = registry.execute_tool("get_current_time")
    print(result)
    
    print("\nTesting Wikipedia search tool:")
    result = registry.execute_tool("search_wikipedia", query="Python programming")
    print(result)
