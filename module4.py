import gradio as gr
import requests
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint (Flask server should be running)
API_URL = os.getenv("API_URL", "http://localhost:5000")

# Generate a session ID for this instance
SESSION_ID = str(uuid.uuid4())

def fetch_models():
    """Fetch available models from the API"""
    try:
        response = requests.get(f"{API_URL}/api/models")
        response.raise_for_status()
        models_data = response.json()

        # Return as list of tuples (name, id) for gradio dropdown
        return [(model["name"], model["id"]) for model in models_data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return [("Llama 3 (70B)", "llama3-70b-8192")]  # Default fallback

def chat_with_api(message, history, model_name):
    """Send message to API and get response"""
    if not message:
        return "", history

    try:
        # Prepare request data
        data = {
            "message": message,
            "session_id": SESSION_ID,
            "model": model_name
        }

        # Send request to API
        response = requests.post(f"{API_URL}/api/chat", json=data)
        response.raise_for_status()
        result = response.json()

        # Extract response
        bot_message = result.get("response", "Sorry, I couldn't process that request.")

        # For Gradio 3.50.2, history needs to be a list of tuples (user_msg, bot_msg)
        # Add the new message pair to history
        history.append((message, bot_message))

        # Return empty message and updated history
        return "", history

    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)

        # Add error message to history
        history.append((message, error_message))
        return "", history
def clear_conversation():
    """Clear the conversation history on the API server"""
    try:
        # Prepare request data
        data = {
            "session_id": SESSION_ID
        }

        # Send request to API
        response = requests.post(f"{API_URL}/api/clear", json=data)
        response.raise_for_status()

        # Return empty history (for Gradio 3.50.2, this should be an empty list)
        return []

    except Exception as e:
        print(f"Error clearing conversation: {e}")
        return []

# Create Gradio interface
def create_chatbot_interface():
    # Fetch available models
    models = fetch_models()
    default_model = models[0][1] if models else "llama3-70b-8192"

    # Create the interface
    with gr.Blocks(title="Groq Chatbot") as interface:
        gr.Markdown("# Groq Chatbot")
        gr.Markdown("Chat with various LLM models powered by Groq")

        with gr.Row():
            with gr.Column(scale=4):
                # Model selection dropdown
                model_dropdown = gr.Dropdown(
                    choices=models,
                    value=default_model,
                    label="Select Model"
                )

            with gr.Column(scale=1):
                # Clear button
                clear_btn = gr.Button("Clear Conversation")

        # Chat interface
        chatbot = gr.Chatbot(height=500)
        msg = gr.Textbox(
            placeholder="Type your message here...",
            label="Your Message",
            scale=4
        )
        submit_btn = gr.Button("Send", variant="primary")

        # Set up event handlers
        submit_btn.click(
            chat_with_api,
            inputs=[msg, chatbot, model_dropdown],
            outputs=[msg, chatbot]
        )

        msg.submit(
            chat_with_api,
            inputs=[msg, chatbot, model_dropdown],
            outputs=[msg, chatbot]
        )

        clear_btn.click(
            lambda: clear_conversation(),
            outputs=[chatbot]
        )

    return interface

# Launch the app
if __name__ == "__main__":
    create_chatbot_interface().launch(share=True)