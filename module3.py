from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dictionary to store conversations for different sessions
conversations = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API endpoint to handle chat requests.
    
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
            
        # Initialize conversation history for new sessions
        if session_id not in conversations:
            conversations[session_id] = [
                {"role": "system", "content": "You are a helpful AI assistant."}
            ]
            
        # Add user message to conversation history
        conversations[session_id].append({"role": "user", "content": message})
        
        # Prepare API request to Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        groq_data = {
            "model": model,
            "messages": conversations[session_id],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        # Send request to Groq API
        response = requests.post(url, headers=headers, json=groq_data)
        response.raise_for_status()
        result = response.json()
        
        # Extract assistant's response
        assistant_message = result["choices"][0]["message"]["content"]
        
        # Add assistant response to conversation history
        conversations[session_id].append({"role": "assistant", "content": assistant_message})
        
        # Return response to client
        return jsonify({
            "response": assistant_message,
            "session_id": session_id,
            "model": model
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500
    except Exception as e:
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
            
        # Clear the conversation history for the session
        if session_id in conversations:
            conversations[session_id] = [
                {"role": "system", "content": "You are a helpful AI assistant."}
            ]
            
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

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """API endpoint to get active sessions."""
    session_list = []
    for session_id in conversations:
        # Count messages (excluding system message)
        message_count = len([msg for msg in conversations[session_id] if msg["role"] != "system"])
        
        # Only include sessions with at least one user message
        if message_count > 0:
            session_list.append({
                "id": session_id,
                "message_count": message_count
            })
    
    return jsonify(session_list)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Groq Chatbot API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)