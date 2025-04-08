from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import uuid
import json
import time
from collections import deque

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dictionary to store conversations with various memory strategies
conversations = {}

class TokenCounter:
    """Utility class to estimate token counts in messages"""
    
    @staticmethod
    def estimate_tokens(text):
        """
        Estimate the number of tokens in a text string.
        This is a rough estimate: ~4 characters per token for English text.
        
        Args:
            text (str): The text to estimate
            
        Returns:
            int: Estimated number of tokens
        """
        return len(text) // 4
    
    @staticmethod
    def count_message_tokens(message):
        """
        Count tokens in a message dictionary.
        
        Args:
            message (dict): Message with role and content
            
        Returns:
            int: Estimated token count
        """
        # Count role (~2 tokens) plus content
        return 2 + TokenCounter.estimate_tokens(message["content"])
    
    @staticmethod
    def count_conversation_tokens(messages):
        """
        Count tokens in a full conversation.
        
        Args:
            messages (list): List of message dictionaries
            
        Returns:
            int: Total estimated token count
        """
        return sum(TokenCounter.count_message_tokens(msg) for msg in messages)


class ConversationMemory:
    """Base class for conversation memory strategies"""
    
    def __init__(self, system_message="You are a helpful AI assistant."):
        """Initialize with a system message"""
        self.system_message = system_message
        self.messages = [{"role": "system", "content": system_message}]
        self.created_at = time.time()
        self.last_updated = time.time()
    
    def add_message(self, role, content):
        """
        Add a message to the conversation history.
        
        Args:
            role (str): Message role (user or assistant)
            content (str): Message content
        """
        self.messages.append({"role": role, "content": content})
        self.last_updated = time.time()
    
    def get_messages(self):
        """Return all messages"""
        return self.messages
    
    def clear(self):
        """Clear all messages except system message"""
        self.messages = [{"role": "system", "content": self.system_message}]
    
    def get_token_count(self):
        """Get estimated token count of conversation"""
        return TokenCounter.count_conversation_tokens(self.messages)


class WindowMemory(ConversationMemory):
    """Conversation memory that keeps a sliding window of messages"""
    
    def __init__(self, system_message="You are a helpful AI assistant.", window_size=10, max_tokens=4000):
        """
        Initialize with a window size and token limit.
        
        Args:
            system_message (str): The system message
            window_size (int): Maximum number of messages to keep
            max_tokens (int): Maximum total tokens to maintain
        """
        super().__init__(system_message)
        self.window_size = window_size
        self.max_tokens = max_tokens
        self.full_history = []  # Store all messages for reference
    
    def add_message(self, role, content):
        """Add message and trim if needed"""
        message = {"role": role, "content": content}
        
        # Add to full history
        self.full_history.append(message)
        
        # Add to current messages
        self.messages.append(message)
        self.last_updated = time.time()
        
        # Trim if needed (always keep system message)
        self._trim_to_window()
        self._trim_to_tokens()
    
    def _trim_to_window(self):
        """Trim messages to the window size"""
        if len(self.messages) > self.window_size + 1:  # +1 for system message
            # Keep system message and last N messages
            self.messages = [self.messages[0]] + self.messages[-(self.window_size):]
    
    def _trim_to_tokens(self):
        """Trim messages to stay under token limit"""
        while self.get_token_count() > self.max_tokens and len(self.messages) > 2:  # Keep at least system + 1 message
            # Remove oldest non-system message
            self.messages.pop(1)
    
    def get_full_history(self):
        """Return the complete message history"""
        return [{"role": "system", "content": self.system_message}] + self.full_history


class SummaryMemory(ConversationMemory):
    """Conversation memory that periodically summarizes old messages"""
    
    def __init__(self, system_message="You are a helpful AI assistant.", 
                 active_window=6, max_tokens=4000, api_key=None):
        """
        Initialize with active window and summarization settings.
        
        Args:
            system_message (str): The system message
            active_window (int): Number of recent messages to keep in full form
            max_tokens (int): Maximum total tokens to maintain
            api_key (str): API key for generating summaries
        """
        super().__init__(system_message)
        self.active_window = active_window
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.summary = None
        self.summarized_count = 0
    
    def add_message(self, role, content):
        """Add message and summarize if needed"""
        # Add the new message
        super().add_message(role, content)
        
        # Check if we need to summarize
        if self.get_token_count() > self.max_tokens:
            self._create_summary()
    
    def _create_summary(self):
        """Summarize older messages"""
        # Keep system message and active window
        messages_to_summarize = self.messages[1:-self.active_window] if len(self.messages) > self.active_window + 1 else []
        
        if not messages_to_summarize:
            return
        
        # Create conversation text for summary
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages_to_summarize])
        
        # Get summary using the API
        summary = self._generate_summary(conversation_text)
        
        # Update summary count
        self.summarized_count = len(messages_to_summarize)
        
        # Replace summarized messages with summary
        if summary:
            self.summary = summary
            # Update messages to: [system, summary, active_window_messages]
            self.messages = [
                self.messages[0],  # System message
                {"role": "system", "content": f"Previous conversation summary: {summary}"},
                *self.messages[-self.active_window:]  # Active window
            ]
    
    def _generate_summary(self, conversation_text):
        """Generate a summary of the conversation using the API"""
        try:
            # API endpoint
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            # Request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Request body
            data = {
                "model": "llama3-8b-8192",  # Use smaller model for summaries
                "messages": [
                    {"role": "system", "content": "Summarize the following conversation concisely:"},
                    {"role": "user", "content": conversation_text}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            # Send the request
            response = requests.post(url, headers=headers, json=data)
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract and return the generated summary
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
    
    def clear(self):
        """Clear all messages and summary"""
        super().clear()
        self.summary = None
        self.summarized_count = 0


class TokenWindowMemory(ConversationMemory):
    """
    Memory that maintains a token-based window rather than message count.
    Optimizes for maximum context within token limits.
    """
    
    def __init__(self, system_message="You are a helpful AI assistant.", max_tokens=6000):
        """
        Initialize with a maximum token count.
        
        Args:
            system_message (str): The system message
            max_tokens (int): Maximum total tokens to maintain
        """
        super().__init__(system_message)
        self.max_tokens = max_tokens
        # Store system message token count
        self.system_tokens = TokenCounter.count_message_tokens({"role": "system", "content": system_message})
        self.available_tokens = max_tokens - self.system_tokens
    
    def add_message(self, role, content):
        """Add message and trim older messages if token limit exceeded"""
        # Add the new message
        message = {"role": role, "content": content}
        self.messages.append(message)
        self.last_updated = time.time()
        
        # Trim if we exceed token limit
        current_tokens = self.get_token_count()
        
        while current_tokens > self.max_tokens and len(self.messages) > 2:  # Keep system + at least 1 message
            # Remove oldest non-system message
            removed_msg = self.messages.pop(1)
            # Recalculate tokens
            current_tokens = self.get_token_count()


# Create a memory manager to handle different memory strategies
class MemoryManager:
    def __init__(self, api_key):
        self.sessions = {}
        self.api_key = api_key
    
    def get_memory(self, session_id, memory_type="window", system_message="You are a helpful AI assistant."):
        """
        Get or create a memory object for a session.
        
        Args:
            session_id (str): Unique session identifier
            memory_type (str): Type of memory strategy (window, summary, token)
            system_message (str): System message for the conversation
            
        Returns:
            ConversationMemory: The memory object
        """
        if session_id not in self.sessions:
            # Create new memory of the specified type
            if memory_type == "window":
                self.sessions[session_id] = WindowMemory(system_message=system_message)
            elif memory_type == "summary":
                self.sessions[session_id] = SummaryMemory(system_message=system_message, api_key=self.api_key)
            elif memory_type == "token":
                self.sessions[session_id] = TokenWindowMemory(system_message=system_message)
            else:
                # Default to window memory
                self.sessions[session_id] = WindowMemory(system_message=system_message)
        
        return self.sessions[session_id]
    
    def clear_memory(self, session_id):
        """Clear the memory for a session"""
        if session_id in self.sessions:
            self.sessions[session_id].clear()
    
    def delete_session(self, session_id):
        """Delete a session completely"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_session_info(self):
        """Get information about all active sessions"""
        info = []
        for session_id, memory in self.sessions.items():
            info.append({
                "session_id": session_id,
                "memory_type": memory.__class__.__name__,
                "message_count": len(memory.messages) - 1,  # Exclude system message
                "token_count": memory.get_token_count(),
                "created_at": memory.created_at,
                "last_updated": memory.last_updated
            })
        return info

# Create a memory manager
memory_manager = MemoryManager(GROQ_API_KEY)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API endpoint to handle chat requests with advanced memory management.
    
    Expected JSON body:
    {
        "message": "User message here",
        "session_id": "unique_session_id" (optional),
        "memory_type": "window|summary|token" (optional),
        "model": "model_name" (optional),
        "system_message": "Custom system message" (optional)
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
            
        # Get memory type
        memory_type = data.get('memory_type', 'window')
        
        # Get system message
        system_message = data.get('system_message', 'You are a helpful AI assistant.')
        
        # Use provided model or default to llama3-70b-8192
        model = data.get('model', 'llama3-70b-8192')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        # Get or create memory for this session
        memory = memory_manager.get_memory(session_id, memory_type, system_message)
        
        # Add user message to memory
        memory.add_message("user", message)
        
        # Get conversation messages for the API
        messages = memory.get_messages()
        
        # Prepare API request to Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        groq_data = {
            "model": model,
            "messages": messages,
            "temperature": data.get('temperature', 0.7),
            "max_tokens": data.get('max_tokens', 1024)
        }
        
        # Send request to Groq API
        response = requests.post(url, headers=headers, json=groq_data)
        response.raise_for_status()
        result = response.json()
        
        # Extract assistant's response
        assistant_message = result["choices"][0]["message"]["content"]
        
        # Add assistant response to memory
        memory.add_message("assistant", assistant_message)
        
        # Get token counts for information
        token_count = memory.get_token_count()
        
        # Return response to client
        return jsonify({
            "response": assistant_message,
            "session_id": session_id,
            "model": model,
            "memory_type": memory_type,
            "token_count": token_count,
            "memory_size": len(memory.messages) - 1  # Exclude system message
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500
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
            
        # Clear the memory for the session
        memory_manager.clear_memory(session_id)
            
        return jsonify({"status": "success", "message": "Conversation cleared"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """API endpoint to get information about active sessions."""
    try:
        # Get session information
        session_info = memory_manager.get_session_info()
        
        # Sort by last updated
        session_info.sort(key=lambda x: x["last_updated"], reverse=True)
        
        return jsonify(session_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory-types', methods=['GET'])
def get_memory_types():
    """API endpoint to get available memory types."""
    memory_types = [
        {
            "id": "window",
            "name": "Window Memory",
            "description": "Keeps a fixed number of recent messages"
        },
        {
            "id": "summary", 
            "name": "Summary Memory",
            "description": "Summarizes older messages to maintain context while saving tokens"
        },
        {
            "id": "token",
            "name": "Token Window",
            "description": "Optimizes for maximum context within token limits"
        }
    ]
    return jsonify(memory_types)

@app.route('/api/models', methods=['GET'])
def get_models():
    """API endpoint to get available models."""
    # Return list of available models
    models = [
        {"id": "llama3-70b-8192", "name": "Llama 3 (70B)", "context_length": 8192},
        {"id": "llama3-8b-8192", "name": "Llama 3 (8B)", "context_length": 8192},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "context_length": 32768},
        {"id": "gemma-7b-it", "name": "Gemma 7B", "context_length": 8192}
    ]
    return jsonify(models)

@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    """API endpoint to get parameter ranges for a model."""
    try:
        model_id = request.args.get('model', 'llama3-70b-8192')
        
        # Define parameter ranges for all models
        # You can customize these ranges based on model capabilities
        parameter_ranges = {
            "temperature": {
                "min": 0.0,
                "max": 2.0,
                "default": 0.7,
                "step": 0.1
            },
            "top_p": {
                "min": 0.0,
                "max": 1.0,
                "default": 0.9,
                "step": 0.05
            },
            "frequency_penalty": {
                "min": 0.0,
                "max": 2.0,
                "default": 0.0,
                "step": 0.1
            },
            "presence_penalty": {
                "min": 0.0,
                "max": 2.0,
                "default": 0.0,
                "step": 0.1
            },
            "max_tokens": {
                "min": 10,
                "max": 4096,
                "default": 1024,
                "step": 10
            }
        }
        
        return jsonify(parameter_ranges)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Advanced Memory Chatbot API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)