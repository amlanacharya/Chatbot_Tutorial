from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools.python.tool import PythonREPLTool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Import our custom Groq LLM implementation from module8
from module8 import get_llm

def create_agent_with_tools(model_name="llama3-70b-8192"):
    """Create an agent with a set of tools"""
    
    # Initialize the LLM
    llm = get_llm(model_name)
    
    # Define tools
    search = DuckDuckGoSearchRun()
    python_repl = PythonREPLTool()
    
    tools = [
        Tool(
            name="web_search",
            func=search.run,
            description="Useful for searching the internet for current information"
        ),
        Tool(
            name="python_repl",
            func=python_repl.run,
            description="Useful for performing calculations or running Python code"
        ),
        Tool(
            name="weather",
            func=lambda location: requests.get(f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}").json(),
            description="Get current weather for a location"
        )
    ]
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant with access to tools. "
                  "Use them when needed to provide accurate and up-to-date information."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Initialize memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor

def main():
    """Main function to demonstrate agent capabilities"""
    
    # Create the agent
    agent = create_agent_with_tools()
    
    print("🤖 AI Agent initialized with tools! Type 'exit' to quit.")
    print("Available tools:")
    print("- Web search")
    print("- Python calculator")
    print("- Weather information")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            break
        
        try:
            # Run the agent
            response = agent.invoke({"input": user_input})
            print("\nAgent:", response["output"])
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with a different query.")

if __name__ == "__main__":
    main()