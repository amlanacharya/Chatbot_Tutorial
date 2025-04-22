"""
Agent Framework for transforming chatbots into goal-oriented agents.

This module provides the core components for building an agent that can:
1. Plan tasks by breaking them down into steps
2. Execute tools to accomplish those steps
3. Maintain state beyond simple conversation history
4. Make decisions about what actions to take next
"""

import json
import os
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Import the tool registry
from tools import create_default_tool_registry

# Load environment variables
load_dotenv()

# Set up Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AVAILABLE_MODELS = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
DEFAULT_MODEL = "llama3-8b-8192"


class Agent:
    """
    An agent that can plan and execute tasks using tools.

    This agent extends beyond a simple chatbot by adding:
    - Planning capabilities to break down tasks
    - Tool usage to interact with external systems
    - State management beyond conversation history
    - Decision-making logic for autonomous operation
    """

    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.7):
        """
        Initialize the agent with a model and temperature.

        Args:
            model: The LLM model to use
            temperature: The temperature for LLM generation
        """
        self.model = model
        self.temperature = temperature
        self.tool_registry = create_default_tool_registry()

        # Initialize state
        self.reset_state()

    def reset_state(self):
        """Reset the agent's state to its initial values."""
        self.state = {
            "conversation": [],  # Conversation history
            "current_plan": None,  # Current task plan
            "current_step_index": 0,  # Index of the current step in the plan
            "task_completed": False,  # Whether the current task is completed
            "collected_information": {},  # Information collected during task execution
            "working_memory": {}  # Short-term memory for the current task
        }

    def add_message_to_conversation(self, role: str, content: str):
        """
        Add a message to the conversation history.

        Args:
            role: The role of the message sender (user or assistant)
            content: The content of the message
        """
        self.state["conversation"].append({"role": role, "content": content})

    def get_llm_response(self, messages: List[Dict[str, str]],
                         json_mode: bool = False) -> str:
        """
        Get a response from the LLM.

        Args:
            messages: The messages to send to the LLM
            json_mode: Whether to request a JSON response

        Returns:
            The LLM's response as a string
        """
        # API endpoint
        url = "https://api.groq.com/openai/v1/chat/completions"

        # Request headers
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Request body
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 1024
        }

        # Add response format if JSON mode is enabled
        if json_mode:
            data["response_format"] = {"type": "json_object"}

        # Send request to Groq API
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            error_msg = f"Error: {response.status_code}, {response.text}"
            print(error_msg)
            return f"I encountered an error when trying to process your request: {error_msg}"

    def determine_if_task(self, user_input: str) -> bool:
        """
        Determine if the user input is a task request or a question.

        Args:
            user_input: The user's input

        Returns:
            True if the input is a task request, False otherwise
        """
        # Check for common task patterns first
        lower_input = user_input.lower()

        # Direct checks for time and math-related queries
        if any(phrase in lower_input for phrase in ["time", "clock", "hour", "date", "day"]):
            return True

        if any(phrase in lower_input for phrase in ["calculate", "compute", "square", "math", "add", "subtract", "multiply", "divide"]):
            return True

        # For other queries, use the LLM to determine if it's a task
        prompt = f"""
        Determine if the following user input is asking for a task to be completed or just asking a question.

        User input: "{user_input}"

        A task request would be something like "find information about X" or "calculate Y" or "help me with Z".
        A question would be something like "what is X?" or "how does Y work?".

        Tasks often involve actions like calculating, finding, getting current information, or performing operations.
        Specifically, requests about current time, date, or mathematical calculations are always tasks.

        Return JSON with a single field "is_task" set to true or false.
        """

        messages = [{"role": "user", "content": prompt}]
        response = self.get_llm_response(messages, json_mode=True)

        try:
            result = json.loads(response)
            return result.get("is_task", False)
        except:
            # If we can't parse the response, assume it's not a task
            return False

    def plan_task(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Break down a task into steps.

        Args:
            task_description: The description of the task

        Returns:
            A list of steps to complete the task
        """
        # Check for common patterns and create direct plans
        lower_task = task_description.lower()

        # Handle time-related queries
        if any(phrase in lower_task for phrase in ["time", "clock", "hour", "date", "day"]):
            return [
                {"step": 1, "description": "Get the current time", "requires_tool": True, "tool_name": "get_current_time"}
            ]

        # Handle math-related queries
        if "square of" in lower_task and any(c.isdigit() for c in lower_task):
            # Extract the number if possible
            try:
                # Find all numbers in the string
                import re
                numbers = re.findall(r'\d+', lower_task)
                if numbers:
                    num = numbers[0]
                    return [
                        {"step": 1, "description": f"Calculate the square of {num}", "requires_tool": True, "tool_name": "calculator", "expression": f"{num} * {num}"}
                    ]
            except:
                pass

        if any(phrase in lower_task for phrase in ["calculate", "compute", "math", "add", "subtract", "multiply", "divide"]):
            return [
                {"step": 1, "description": "Perform the mathematical calculation", "requires_tool": True, "tool_name": "calculator"}
            ]

        # For other tasks, use the LLM to create a plan
        # Get the list of available tools
        tools_list = self.tool_registry.list_tools()
        tools_json = json.dumps(tools_list, indent=2)

        # Create a planning prompt
        planning_prompt = f"""
        I need to complete this task: {task_description}

        I have the following tools available:
        {tools_json}

        Please break this down into a sequence of steps. For each step, indicate if a tool should be used.
        Return as a JSON list of steps, where each step has:
        - "step": step number
        - "description": what to do in this step
        - "requires_tool": boolean indicating if this step needs a tool
        - "tool_name": (optional) name of the tool to use if requires_tool is true

        Example:
        [
            {{"step": 1, "description": "Understand the user's request", "requires_tool": false}},
            {{"step": 2, "description": "Calculate 25 * 16", "requires_tool": true, "tool_name": "calculator"}}
        ]
        """

        try:
            planning_messages = [{"role": "user", "content": planning_prompt}]
            response = self.get_llm_response(planning_messages, json_mode=True)

            # Parse JSON response
            steps = json.loads(response)
            # Ensure steps is a list of dictionaries
            if isinstance(steps, list):
                # Validate each step is a dictionary
                valid_steps = []
                for i, step in enumerate(steps):
                    if isinstance(step, dict):
                        valid_steps.append(step)
                    else:
                        # Convert string or other types to a dictionary
                        valid_steps.append({
                            "step": i+1,
                            "description": str(step),
                            "requires_tool": False
                        })
                return valid_steps
            else:
                # If steps is not a list, create a default plan
                return [{"step": 1, "description": "Process the user's request", "requires_tool": False}]
        except Exception as e:
            print(f"Error parsing plan: {e}")
            # If we can't parse the response, create a simple plan based on the task
            return [{"step": 1, "description": f"Process the request: {task_description}", "requires_tool": False}]

    def determine_tool_parameters(self, step: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """
        Determine the parameters to use for a tool based on the step.

        Args:
            step: The step dictionary containing the description and any pre-defined parameters
            tool_name: The name of the tool to use

        Returns:
            A dictionary of parameters for the tool
        """
        # Check if the step already has parameters defined
        if tool_name == "calculator" and "expression" in step:
            return {"expression": step["expression"]}

        # For time-related queries, default to local timezone
        if tool_name == "get_current_time":
            return {"timezone": "local"}

        # For other cases, use the LLM to determine parameters
        step_description = step["description"]

        # Get the tool's parameter descriptions
        tool = self.tool_registry.get_tool(tool_name)
        parameters_json = json.dumps(tool["parameters"], indent=2)

        # Create a prompt to determine the parameters
        prompt = f"""
        For the following step in a task:
        "{step_description}"

        I need to use the "{tool_name}" tool, which has these parameters:
        {parameters_json}

        Please determine the appropriate values for these parameters based on the step description.
        Return a JSON object with the parameter names as keys and their values.
        """

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.get_llm_response(messages, json_mode=True)

            parameters = json.loads(response)
            return parameters
        except Exception as e:
            print(f"Error determining parameters: {e}")
            # If we can't parse the response, return default parameters based on the tool
            if tool_name == "calculator":
                # Try to extract a calculation from the description
                import re
                # Look for patterns like "2 + 2" or "square of 99"
                match = re.search(r'\d+\s*[+\-*/^]\s*\d+', step_description)
                if match:
                    return {"expression": match.group(0)}

                if "square of" in step_description.lower():
                    numbers = re.findall(r'\d+', step_description)
                    if numbers:
                        num = numbers[0]
                        return {"expression": f"{num} * {num}"}

                return {"expression": "2 + 2"} # Default fallback

            elif tool_name == "get_current_time":
                return {"timezone": "local"}

            else:
                return {}

    def execute_step(self, step: Dict[str, Any]) -> str:
        """
        Execute a step in the plan.

        Args:
            step: The step to execute

        Returns:
            The result of executing the step
        """
        if step.get("requires_tool", False) and "tool_name" in step:
            # Execute the tool
            tool_name = step["tool_name"]
            parameters = self.determine_tool_parameters(step, tool_name)

            try:
                result = self.tool_registry.execute_tool(tool_name, **parameters)
                return f"Tool result: {result}"
            except Exception as e:
                return f"Error executing tool: {str(e)}"
        else:
            # Use LLM to process this step
            step_prompt = f"""
            Complete this step in a task: {step['description']}

            Based on what you know, provide the information or action needed for this step.
            """

            try:
                step_messages = [{"role": "user", "content": step_prompt}]
                response = self.get_llm_response(step_messages)
                return response
            except Exception as e:
                print(f"Error executing step with LLM: {e}")
                # Provide a direct response if LLM fails
                if "time" in step["description"].lower():
                    import datetime
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return f"The current time is {current_time}"
                elif "square" in step["description"].lower():
                    import re
                    numbers = re.findall(r'\d+', step["description"])
                    if numbers:
                        num = int(numbers[0])
                        return f"The square of {num} is {num * num}"
                return f"Completed step: {step['description']}"

    def generate_task_summary(self) -> str:
        """
        Generate a summary of the completed task.

        Returns:
            A summary of the task execution
        """
        # Create a summary of the plan and results
        plan_json = json.dumps(self.state["current_plan"], indent=2)
        results_json = json.dumps(self.state["collected_information"], indent=2)

        summary_prompt = f"""
        I've completed a task with the following plan:
        {plan_json}

        And collected this information:
        {results_json}

        Please provide a concise summary of what was accomplished and what was learned.
        """

        summary_messages = [{"role": "user", "content": summary_prompt}]
        summary = self.get_llm_response(summary_messages)

        return summary

    def process_user_input(self, user_input: str) -> str:
        """
        Process user input and return a response.

        This is the main entry point for interacting with the agent.

        Args:
            user_input: The user's input

        Returns:
            The agent's response
        """
        # Initialize conversation with a system message if it's empty
        if not self.state["conversation"]:
            system_message = {
                "role": "system",
                "content": "You are an AI assistant with access to tools. You can perform tasks like calculating math expressions and telling the current time. Always use your tools when appropriate instead of making up answers."
            }
            self.state["conversation"].append(system_message)

        # Add the user input to the conversation
        self.add_message_to_conversation("user", user_input)

        # Determine if this is a task request or a question
        is_task = self.determine_if_task(user_input)

        if is_task:
            # Task handling path
            response = "I'll help you complete this task. Let me break it down into steps.\n\n"

            # Plan the task
            self.state["current_plan"] = self.plan_task(user_input)
            self.state["current_step_index"] = 0
            self.state["task_completed"] = False
            self.state["collected_information"] = {}

            # Show the plan
            response += "Here's my plan:\n"
            for i, step in enumerate(self.state["current_plan"]):
                step_num = step.get('step', i+1)
                description = step.get('description', 'Step description not available')
                response += f"- Step {step_num}: {description}\n"

            response += "\nI'll start working on this task. I'll let you know when I'm done."

            # Execute the plan step by step
            step_results = []
            for i, step in enumerate(self.state["current_plan"]):
                self.state["current_step_index"] = i

                step_result = self.execute_step(step)
                step_results.append(step_result)

                # Store the result
                self.state["collected_information"][f"step_{i+1}"] = step_result

            # Mark the task as completed
            self.state["task_completed"] = True

            # Generate a summary
            summary = self.generate_task_summary()

            # Add the results to the response
            response += "\n\nHere are the results of each step:\n"
            for i, result in enumerate(step_results):
                step = self.state['current_plan'][i]
                description = step.get('description', f'Step {i+1}')
                response += f"\nStep {i+1}: {description}\n"
                response += f"Result: {result}\n"

            response += f"\n\nTask completed! Summary:\n{summary}"
        else:
            # Standard chatbot path for questions
            messages = self.state["conversation"].copy()
            response = self.get_llm_response(messages)

        # Add the response to the conversation
        self.add_message_to_conversation("assistant", response)

        return response


if __name__ == "__main__":
    # Test the agent
    agent = Agent()

    # Process a task
    response = agent.process_user_input("Calculate the square root of 144 and then tell me what time it is.")
    print("Response to task:")
    print(response)
    print("\n" + "-"*50 + "\n")

    # Process a question
    response = agent.process_user_input("What's the difference between a chatbot and an agent?")
    print("Response to question:")
    print(response)
