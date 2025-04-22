# Module 14: Exercises

These exercises will help you practice and extend the concepts covered in Module 14: From Chatbots to Agents.

## Exercise 1: Add a New Tool

**Objective:** Create and register a new tool for the agent to use.

1. Open `tools.py` and create a new function for your tool. Some ideas:
   - A weather tool that fetches current weather data
   - A translation tool that translates text between languages
   - A note-taking tool that saves and retrieves notes

2. Register your new tool in the `create_default_tool_registry` function.

3. Test your tool by running the agent and asking it to use your new tool.

**Example implementation for a note-taking tool:**

```python
# In tools.py

# Add this to the imports
import os
from datetime import datetime

# Add this function
def save_note(title: str, content: str) -> str:
    """
    Save a note to a file.
    
    Args:
        title: The title of the note
        content: The content of the note
        
    Returns:
        A confirmation message
    """
    # Create a notes directory if it doesn't exist
    if not os.path.exists("notes"):
        os.makedirs("notes")
    
    # Create a filename from the title
    filename = f"notes/{title.replace(' ', '_').lower()}.txt"
    
    # Add a timestamp to the note
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_content = f"# {title}\nCreated: {timestamp}\n\n{content}"
    
    # Save the note
    with open(filename, "w") as f:
        f.write(full_content)
    
    return f"Note '{title}' saved successfully to {filename}"

# In the create_default_tool_registry function, add:
registry.register_tool(
    name="save_note",
    description="Save a note to a file",
    function=save_note,
    parameters=[
        {
            "name": "title",
            "type": "string",
            "description": "The title of the note"
        },
        {
            "name": "content",
            "type": "string",
            "description": "The content of the note"
        }
    ]
)
```

## Exercise 2: Improve the Planning System

**Objective:** Enhance the agent's planning capabilities to handle more complex tasks.

1. Modify the `plan_task` method in `agent_framework.py` to include:
   - Dependencies between steps (which steps must be completed before others)
   - Estimated time for each step
   - Confidence level for each step

2. Update the `execute_step` method to handle these new planning features.

3. Test your improved planning system with a complex multi-step task.

## Exercise 3: Add Memory Persistence

**Objective:** Implement a persistent memory system for the agent.

1. Create a new file called `memory.py` with classes for different types of memory:
   - Short-term memory (conversation history)
   - Long-term memory (facts and information)
   - Working memory (current task state)

2. Implement methods to save and load memory from disk.

3. Integrate your memory system with the agent framework.

4. Test that the agent can remember information across different sessions.

## Exercise 4: Implement Self-Reflection

**Objective:** Add self-reflection capabilities to the agent.

1. Create a new method in the `Agent` class called `reflect_on_task` that:
   - Analyzes the steps taken to complete a task
   - Identifies what went well and what could be improved
   - Suggests improvements for future similar tasks

2. Call this method after completing a task.

3. Update the task summary to include the reflection.

4. Test the reflection system with different types of tasks.

## Exercise 5: Create a Multi-Agent System

**Objective:** Build a system with multiple specialized agents that can collaborate.

1. Create a new file called `multi_agent.py` that defines different agent roles:
   - Planner agent (breaks down tasks)
   - Research agent (gathers information)
   - Execution agent (carries out actions)
   - Critic agent (evaluates results)

2. Implement a coordination mechanism for the agents to communicate.

3. Create a main loop that orchestrates the agents' collaboration.

4. Test the multi-agent system on a complex task that requires different skills.

## Submission Guidelines

For each exercise:
1. Create a separate Python file with your implementation
2. Include comments explaining your code
3. Write a brief summary of what you learned
4. Include examples of the agent using your new features

## Bonus Challenge: Agent Evaluation Framework

Create an evaluation framework that can:
1. Run the agent on a set of predefined tasks
2. Measure performance metrics (success rate, time to completion, etc.)
3. Compare different agent configurations
4. Generate a report with the results

This will help you systematically improve your agent design based on empirical data.
