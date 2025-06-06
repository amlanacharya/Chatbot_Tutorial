import streamlit as st
import requests
import json
import uuid
import os
import pandas as pd
import plotly.express as px
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint (Flask server should be running)
API_URL = os.getenv("API_URL", "http://localhost:5000")

# Set page configuration
st.set_page_config(
    page_title="Model Comparison and Tuning",
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
    
if "parameters" not in st.session_state:
    st.session_state.parameters = {}

if "models_info" not in st.session_state:
    st.session_state.models_info = {}

if "parameter_ranges" not in st.session_state:
    st.session_state.parameter_ranges = {}

if "comparison_results" not in st.session_state:
    st.session_state.comparison_results = None

# Function to fetch available models from the API
def fetch_models():
    """Fetch available models and their information from the API"""
    try:
        response = requests.get(f"{API_URL}/api/models")
        response.raise_for_status()
        models_data = response.json()
        
        # Store full model info
        st.session_state.models_info = {model["id"]: model for model in models_data}
        
        # Return as dict for streamlit selectbox
        return {model["name"]: model["id"] for model in models_data}
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return {"Llama 3 (70B)": "llama3-70b-8192"}  # Default fallback

# Function to fetch parameter ranges for the current model
def fetch_parameter_ranges(model_id):
    """Fetch parameter ranges for a specific model"""
    try:
        response = requests.get(f"{API_URL}/api/parameters?model={model_id}")
        response.raise_for_status()
        st.session_state.parameter_ranges = response.json()
        
        # Initialize parameters with defaults if not set
        if not st.session_state.parameters:
            st.session_state.parameters = {
                param: info["default"] 
                for param, info in st.session_state.parameter_ranges.items()
            }
    except Exception as e:
        st.error(f"Error fetching parameter ranges: {e}")
        # Set some defaults
        st.session_state.parameter_ranges = {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.7, "step": 0.1}
        }

# Function to send message to the API
def chat_with_api(message):
    """Send message to API and get response"""
    try:
        # Prepare request data
        data = {
            "message": message,
            "session_id": st.session_state.session_id,
            "model": st.session_state.model,
            "parameters": st.session_state.parameters
        }
        
        # Send request to API
        with st.spinner("AI is thinking..."):
            response = requests.post(f"{API_URL}/api/chat", json=data)
            response.raise_for_status()
            result = response.json()
        
        # Extract response and stats
        assistant_message = result.get("response", "Sorry, I couldn't process that request.")
        stats = result.get("stats", {})
        
        return assistant_message, stats
    
    except Exception as e:
        return f"Error: {str(e)}", {}

# Function to clear conversation history
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

# Function to update model parameters
def update_parameters():
    """Update parameters for the current session"""
    try:
        # Prepare request data
        data = {
            "session_id": st.session_state.session_id,
            "parameters": st.session_state.parameters
        }
        
        # Send request to API
        response = requests.post(f"{API_URL}/api/update-parameters", json=data)
        response.raise_for_status()
        
    except Exception as e:
        st.error(f"Error updating parameters: {e}")

# Function to change the model
def change_model(new_model_id):
    """Change the model for the current session"""
    try:
        # Prepare request data
        data = {
            "session_id": st.session_state.session_id,
            "model": new_model_id
        }
        
        # Send request to API
        response = requests.post(f"{API_URL}/api/change-model", json=data)
        response.raise_for_status()
        
        # Update local model and parameters
        result = response.json()
        st.session_state.model = new_model_id
        st.session_state.parameters = result.get("parameters", {})
        
        # Fetch parameter ranges for the new model
        fetch_parameter_ranges(new_model_id)
        
    except Exception as e:
        st.error(f"Error changing model: {e}")

# Function to compare models
def compare_models(prompt, models_to_compare, system_message, parameters):
    """Compare multiple models on the same prompt"""
    try:
        # Prepare request data
        data = {
            "prompt": prompt,
            "models": models_to_compare,
            "system_message": system_message,
            "parameters": parameters
        }
        
        # Send request to API
        with st.spinner("Comparing models..."):
            response = requests.post(f"{API_URL}/api/compare-models", json=data)
            response.raise_for_status()
            result = response.json()
        
        # Store comparison results
        st.session_state.comparison_results = result
        
    except Exception as e:
        st.error(f"Error comparing models: {e}")
        st.session_state.comparison_results = None

# Function to get model performance stats
def get_performance_stats():
    """Get performance statistics for models"""
    try:
        response = requests.get(f"{API_URL}/api/performance")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching performance data: {e}")
        return None

# Initialize by fetching models and parameter ranges
models_dict = fetch_models()
fetch_parameter_ranges(st.session_state.model)

# Handle model change
def handle_model_change():
    """Handler for model change"""
    # Get the model ID from the selected model name
    model_name = st.session_state.model_selector
    new_model_id = models_dict[model_name]
    
    # Update model if changed
    if new_model_id != st.session_state.model:
        change_model(new_model_id)

# Main function
def main():
    # Set up page with tabs for different functionality
    tab1, tab2, tab3 = st.tabs(["Chat", "Model Comparison", "Performance Metrics"])
    
    # Sidebar for settings
    with st.sidebar:
        st.title("Model Settings")
        
        # Model selection in sidebar
        st.selectbox(
            "Select Model",
            options=list(models_dict.keys()),
            index=list(models_dict.values()).index(st.session_state.model) if st.session_state.model in models_dict.values() else 0,
            key="model_selector",
            on_change=handle_model_change
        )
        
        # Show model information
        if st.session_state.model in st.session_state.models_info:
            model_info = st.session_state.models_info[st.session_state.model]
            st.markdown(f"**Context Length:** {model_info.get('context_length', 'Unknown')}")
            st.markdown("**Strengths:**")
            for strength in model_info.get('strengths', ['Unknown']):
                st.markdown(f"- {strength}")
        
        # Parameter tuning
        st.divider()
        st.subheader("Parameter Tuning")
        
        # Temperature slider
        if "temperature" in st.session_state.parameter_ranges:
            temp_range = st.session_state.parameter_ranges["temperature"]
            st.session_state.parameters["temperature"] = st.slider(
                "Temperature",
                min_value=temp_range["min"],
                max_value=temp_range["max"],
                value=st.session_state.parameters.get("temperature", temp_range["default"]),
                step=temp_range["step"],
                help="Higher values make output more random, lower values more deterministic"
            )
        
        # Top-p slider
        if "top_p" in st.session_state.parameter_ranges:
            top_p_range = st.session_state.parameter_ranges["top_p"]
            st.session_state.parameters["top_p"] = st.slider(
                "Top-p (Nucleus Sampling)",
                min_value=top_p_range["min"],
                max_value=top_p_range["max"],
                value=st.session_state.parameters.get("top_p", top_p_range["default"]),
                step=top_p_range["step"],
                help="Controls diversity. 0.9 means consider only tokens comprising the top 90% probability mass"
            )
        
        # Frequency penalty slider
        if "frequency_penalty" in st.session_state.parameter_ranges:
            freq_range = st.session_state.parameter_ranges["frequency_penalty"]
            st.session_state.parameters["frequency_penalty"] = st.slider(
                "Frequency Penalty",
                min_value=freq_range["min"],
                max_value=freq_range["max"],
                value=st.session_state.parameters.get("frequency_penalty", freq_range["default"]),
                step=freq_range["step"],
                help="Reduces repetition by penalizing tokens that have already appeared in the text"
            )
        
        # Update parameters button
        if st.button("Update Parameters"):
            update_parameters()
            st.success("Parameters updated successfully!")
        
        # Add clear button to sidebar
        st.divider()
        if st.button("Clear Conversation"):
            clear_conversation()
            st.experimental_rerun()
        
        # Display session ID
        st.caption(f"Session ID: {st.session_state.session_id}")
    
    # Tab 1: Chat Interface
    with tab1:
        st.header("Chat with Model")
        
        # Display current parameter settings
        with st.expander("Current Parameter Settings"):
            for param, value in st.session_state.parameters.items():
                st.write(f"**{param}:** {value}")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    assistant_response, stats = chat_with_api(prompt)
                    st.markdown(assistant_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        # In the main() function, after handling tab1 (and tab2 if implemented)
    with tab3:
        st.header("Performance Metrics")
        
        # Fetch performance data
        with st.spinner("Loading performance data..."):
            performance_data = get_performance_stats()
        
        if performance_data:
            # Create columns for different metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Response Times")
                # Create a DataFrame for response times
                response_times = {
                    model: data["avg_response_time"] 
                    for model, data in performance_data.items()
                }
                df_times = pd.DataFrame({
                    "Model": list(response_times.keys()),
                    "Avg Response Time (s)": list(response_times.values())
                })
                
                # Create a bar chart
                fig = px.bar(
                    df_times, 
                    x="Model", 
                    y="Avg Response Time (s)",
                    title="Average Response Time by Model",
                    color="Model"
                )
                st.plotly_chart(fig)
            
            with col2:
                st.subheader("Usage")
                # Create a DataFrame for usage
                usage = {
                    model: data["usage"]["requests"] 
                    for model, data in performance_data.items()
                }
                df_usage = pd.DataFrame({
                    "Model": list(usage.keys()),
                    "Requests": list(usage.values())
                })
                
                # Create a pie chart
                fig = px.pie(
                    df_usage, 
                    values="Requests", 
                    names="Model",
                    title="Request Distribution by Model"
                )
                st.plotly_chart(fig)
            
            # Token usage table
            st.subheader("Token Usage")
            token_usage = {
                model: data["usage"]["tokens"]
                for model, data in performance_data.items()
            }
            df_tokens = pd.DataFrame({
                "Model": list(token_usage.keys()),
                "Tokens Used": list(token_usage.values())
            })
            st.dataframe(df_tokens)
        else:
            st.info("No performance data available yet. Try sending some messages first.")
    with tab2:
        st.header("Model Comparison")
        
        # Create a form for the comparison input
        with st.form("comparison_form"):
            # Prompt input
            comparison_prompt = st.text_area(
                "Enter a prompt to test across multiple models:",
                height=100,
                placeholder="Write a prompt here to compare how different models respond..."
            )
            
            # System message (optional)
            system_message = st.text_input(
                "System message (optional):",
                value="You are a helpful AI assistant.",
                help="This sets the behavior context for the AI models."
            )
            
            # Model selection
            available_models = list(models_dict.values())
            selected_models = st.multiselect(
                "Select models to compare:",
                options=available_models,
                default=[available_models[0]] if available_models else [],
                format_func=lambda x: next((m["name"] for m in st.session_state.models_info.values() if m["id"] == x), x)
            )
            
            # Parameter settings for comparison
            st.subheader("Parameters for comparison")
            comp_temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1
            )
            
            # Submit button
            submit_button = st.form_submit_button("Compare Models")
        
        # Handle form submission
        if submit_button and comparison_prompt and selected_models:
            # Create parameters dictionary
            parameters = {
                "temperature": comp_temperature,
                "max_tokens": 1024
            }
            
            # Call the API to compare models
            with st.spinner("Comparing models..."):
                try:
                    compare_models(comparison_prompt, selected_models, system_message, parameters)
                except Exception as e:
                    st.error(f"Error comparing models: {e}")
        
        # Display comparison results if available
        if st.session_state.comparison_results:
            st.subheader("Comparison Results")
            
            # Get the prompt
            prompt = st.session_state.comparison_results.get("prompt", "")
            st.write(f"**Prompt:** {prompt}")
            
            # Display results in tabs for each model
            model_tabs = st.tabs([
                st.session_state.models_info.get(result["model"], {}).get("name", result["model"]) 
                for result in st.session_state.comparison_results.get("results", [])
            ])
            
            # Fill each tab with the model's response
            for i, tab in enumerate(model_tabs):
                results = st.session_state.comparison_results.get("results", [])
                if i < len(results):
                    result = results[i]
                    with tab:
                        st.markdown("### Response")
                        st.markdown(result.get("response", "No response"))
                        
                        # Display metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Response Time", f"{result.get('response_time', 0):.2f} sec")
                        with col2:
                            st.metric("Token Count", result.get("token_count", 0))
            
            # Create a comparison table
            st.subheader("Performance Comparison")
            comparison_data = []
            for result in st.session_state.comparison_results.get("results", []):
                model_name = st.session_state.models_info.get(result["model"], {}).get("name", result["model"])
                comparison_data.append({
                    "Model": model_name,
                    "Response Time (s)": round(result.get("response_time", 0), 3),
                    "Token Count": result.get("token_count", 0)
                })
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                st.dataframe(df)
                
                # Create a bar chart for response times
                fig1 = px.bar(
                    df, 
                    x="Model", 
                    y="Response Time (s)",
                    title="Response Time Comparison",
                    color="Model"
                )
                st.plotly_chart(fig1)
                
                # Create a bar chart for token counts
                fig2 = px.bar(
                    df, 
                    x="Model", 
                    y="Token Count",
                    title="Token Count Comparison",
                    color="Model"
                )
                st.plotly_chart(fig2)
        else:
            st.info("Enter a prompt and select models to compare their responses.")
if __name__ == "__main__":
    main()  