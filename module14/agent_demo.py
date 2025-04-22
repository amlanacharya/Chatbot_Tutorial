"""
Agent Demo Script

This script demonstrates the agent framework in action with a simple command-line interface.
It allows users to interact with the agent and see how it handles both task requests and questions.
"""

import os
import sys
import time
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the agent_framework module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent framework
from module14.agent_framework import Agent, AVAILABLE_MODELS

def print_with_typing_effect(text: str, delay: float = 0.01):
    """
    Print text with a typing effect to simulate the agent thinking and responding.
    
    Args:
        text: The text to print
        delay: The delay between characters in seconds
    """
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_header():
    """Print the demo header."""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🤖 AI Agent Demo - From Chatbots to Agents                 ║
    ║                                                              ║
    ║   Type your questions or tasks, or 'exit' to quit            ║
    ║   Try asking for tasks like:                                 ║
    ║   - "Calculate the square root of 144"                       ║
    ║   - "Tell me what time it is and then search for Python"     ║
    ║   - "Help me plan a trip to New York"                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(header)


def print_agent_thinking():
    """Print a thinking animation."""
    thinking_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    print("Agent is thinking ", end="", flush=True)
    
    for _ in range(10):
        for frame in thinking_frames:
            print(f"\rAgent is thinking {frame}", end="", flush=True)
            time.sleep(0.1)
    
    print("\r" + " " * 30 + "\r", end="", flush=True)


def select_model() -> str:
    """
    Allow the user to select a model from the available models.
    
    Returns:
        The selected model name
    """
    print("Available models:")
    for i, model in enumerate(AVAILABLE_MODELS):
        print(f"{i+1}. {model}")
    
    while True:
        try:
            choice = int(input("\nSelect a model (or press Enter for default): ") or "1")
            if 1 <= choice <= len(AVAILABLE_MODELS):
                return AVAILABLE_MODELS[choice-1]
            else:
                print(f"Please enter a number between 1 and {len(AVAILABLE_MODELS)}")
        except ValueError:
            print("Please enter a valid number")


def main():
    """Run the agent demo."""
    print_header()
    
    # Let the user select a model
    model = select_model()
    print(f"\nUsing model: {model}\n")
    
    # Create the agent
    agent = Agent(model=model)
    
    # Main interaction loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check if the user wants to exit
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the AI Agent Demo. Goodbye!")
            break
        
        # Process the user input
        print_agent_thinking()
        response = agent.process_user_input(user_input)
        
        # Print the response with a typing effect
        print("\nAgent:", end=" ")
        print_with_typing_effect(response)


if __name__ == "__main__":
    main()
