import streamlit as st
import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint (Flask server should be running)
API_URL = os.getenv("API_URL", "http://localhost:5000")

# Set page configuration
st.set_page_config(
    page_title="Groq Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = "llama3-70b-8192"

def fetch_models():
    """Fetch available models from the API"""
    try:
        response = requests.get(f"{API_URL}/api/models")
        response.raise_for_status()
        models_data = response.json()
        
        # Return as dict for streamlit selectbox
        return {model["name"]: model["id"] for model in models_data}
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return {"Llama 3 (70B)": "llama3-70b-8192"}  # Default fallback

def chat_with_api(message):
    """Send message to API and get response"""
    try:
        # Prepare request data
        data = {
            "message": message,
            "session_id": st.session_state.session_id,
            "model": st.session_state.model
        }
        
        # Send request to API
        with st.spinner("AI is thinking..."):
            response = requests.post(f"{API_URL}/api/chat", json=data)
            response.raise_for_status()
            result = response.json()
        
        # Extract response
        return result.get("response", "Sorry, I couldn't process that request.")
    
    except Exception as e:
        return f"Error: {str(e)}"

def clear_conversation():
    """Clear the conversation history on the API server"""
    try:
        # Prepare request data
        data = {
            "session_id": st.session_state.session_id
        }
        
        # Send request to API
        response = requests.post(f"{API_URL}/api/clear", json=data)
        response.raise_for_status()
        
        # Clear local message history
        st.session_state.messages = []
        
    except Exception as e:
        st.error(f"Error clearing conversation: {e}")

def handle_model_change():
    """Handler for model change"""
    # Get the model ID from the selected model name
    model_name = st.session_state.model_selector
    st.session_state.model = models_dict[model_name]

def main():
    # App header
    st.title("Groq Chatbot")
    
    # Sidebar for settings
    st.sidebar.title("Settings")
    
    # Fetch available models
    models_dict = fetch_models()
    model_names = list(models_dict.keys())
    
    # Model selection in sidebar
    st.sidebar.selectbox(
        "Select Model",
        options=model_names,
        index=0 if "Llama 3 (70B)" in model_names else 0,
        key="model_selector",
        on_change=handle_model_change
    )
    
    # Add clear button to sidebar
    if st.sidebar.button("Clear Conversation"):
        clear_conversation()
        st.experimental_run()
    
    # Display session ID in sidebar
    st.sidebar.divider()
    st.sidebar.caption(f"Session ID: {st.session_state.session_id}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.chat_message("user").write(prompt)
        
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get AI response
        response = chat_with_api(prompt)
        
        # Display AI response
        with st.chat_message("assistant"):
            st.write(response)
        
        # Add to session state
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()