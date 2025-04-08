from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import uuid
import requests

# Import LangChain components
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManager
from typing import Any, List, Mapping, Optional, Union, Dict

# Load environment variables
load_dotenv()

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dictionary to store conversation chains for different sessions
conversation_chains = {}

# Custom Groq Chat model implementation
class GroqLLM(LLM):
    """Custom implementation of a chat model for Groq"""
    
    model_name: str = "llama3-70b-8192"
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    groq_api_key: str = None
    
    def __init__(self, groq_api_key=None, model_name="llama3-70b-8192", temperature=0.7, max_tokens=1024, top_p=0.9):
        """Initialize with model parameters"""
        super().__init__()
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        
        # Ensure API key is set
        if not self.groq_api_key:
            raise ValueError("groq_api_key must be provided")
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate a response from the model."""
        # Prepare API request
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
        
        # Add stop sequences if provided
        if stop:
            data["stop"] = stop
            
        # Send request to Groq API
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Return the content
        return result["choices"][0]["message"]["content"]
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "groq"

    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

def get_llm(model_name="llama3-70b-8192"):
    """Create and return a Groq LLM instance"""
    return GroqLLM(
        groq_api_key=GROQ_API_KEY,
        model_name=model_name,
        temperature=0.7,
    )

def get_conversation_chain(session_id, model_name="llama3-70b-8192"):
    """Get or create a conversation chain for a session"""
    if session_id not in conversation_chains:
        llm = get_llm(model_name)
        
        # Create memory for storing conversation history
        memory = ConversationBufferMemory()
        
        # Create the conversation chain
        chain = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True
        )
        
        conversation_chains[session_id] = {
            "chain": chain,
            "model": model_name
        }
    
    # If model has changed, update the chain
    elif conversation_chains[session_id]["model"] != model_name:
        # Get the existing memory
        existing_memory = conversation_chains[session_id]["chain"].memory
        
        # Create new LLM with updated model
        llm = get_llm(model_name)
        
        # Create new chain with existing memory
        chain = ConversationChain(
            llm=llm,
            memory=existing_memory,
            verbose=True
        )
        
        # Update the conversation chain
        conversation_chains[session_id] = {
            "chain": chain,
            "model": model_name
        }
    
    return conversation_chains[session_id]["chain"]

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API endpoint to handle chat requests using LangChain.
    
    Expected JSON body:
    {
        "message": "User message here",
        "session_id": "unique_session_id" (optional),
        "model": "model_name" (optional)
    }
    """
    try:
        # Get request data
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        message = data.get('message')
        
        # Use provided session_id or generate a new one
        session_id = data.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Use provided model or default to llama3-70b-8192
        model = data.get('model', 'llama3-70b-8192')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get or create conversation chain
        chain = get_conversation_chain(session_id, model)
        
        # Process the message with LangChain
        response = chain.predict(input=message)
        
        # Return response to client
        return jsonify({
            "response": response,
            "session_id": session_id,
            "model": model
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """
    API endpoint to clear conversation history.
    
    Expected JSON body:
    {
        "session_id": "session_id_to_clear"
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"error": "No session ID provided"}), 400
            
        # Clear the conversation chain for the session
        if session_id in conversation_chains:
            # Reset the memory
            conversation_chains[session_id]["chain"].memory.clear()
            
        return jsonify({"status": "success", "message": "Conversation cleared"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """API endpoint to get available models."""
    # Return list of available models
    models = [
        {"id": "llama3-70b-8192", "name": "Llama 3 (70B)"},
        {"id": "llama3-8b-8192", "name": "Llama 3 (8B)"},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B"},
        {"id": "gemma-7b-it", "name": "Gemma 7B"}
    ]
    return jsonify(models)

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """
    API endpoint to get chat history for a session.
    
    Expected query parameters:
    session_id: The session ID to get history for
    """
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({"error": "No session ID provided"}), 400
            
        if session_id not in conversation_chains:
            return jsonify({"messages": []})
            
        # Get the conversation memory
        memory = conversation_chains[session_id]["chain"].memory
        
        # For standard ConversationBufferMemory, extract history in a simple format
        messages = []
        
        # Get the raw buffer and parse it manually
        buffer = memory.buffer
        # Simple parsing - this is a heuristic approach
        lines = buffer.split('\n')
        for line in lines:
            if line.startswith('Human:'):
                messages.append({
                    "role": "user",
                    "content": line.replace('Human:', '').strip()
                })
            elif line.startswith('AI:'):
                messages.append({
                    "role": "assistant",
                    "content": line.replace('AI:', '').strip()
                })
                
        return jsonify({"messages": messages})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting LangChain Chatbot API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)