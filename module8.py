from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import uuid

# Import LangChain components
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage

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

def get_llm(model_name="llama3-70b-8192"):
    """Create and return a Groq LLM instance"""
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=model_name,
        temperature=0.7,
    )

def get_conversation_chain(session_id, model_name="llama3-70b-8192"):
    """Get or create a conversation chain for a session"""
    if session_id not in conversation_chains:
        llm = get_llm(model_name)
        
        # Create a prompt template that includes conversation history
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant that provides accurate and concise information."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Create memory for storing conversation history
        memory = ConversationBufferMemory(return_messages=True, memory_key="history")
        
        # Create the conversation chain
        chain = ConversationChain(
            llm=llm,
            prompt=prompt,
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
        
        # Create a prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant that provides accurate and concise information."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Create new chain with existing memory
        chain = ConversationChain(
            llm=llm,
            prompt=prompt,
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
        
        # Convert memory to a list of messages
        messages = []
        
        for message in memory.chat_memory.messages:
            if hasattr(message, 'content') and hasattr(message, 'type'):
                role = "assistant" if message.type == "ai" else "user"
                messages.append({
                    "role": role,
                    "content": message.content
                })
                
        return jsonify({"messages": messages})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting LangChain Chatbot API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)