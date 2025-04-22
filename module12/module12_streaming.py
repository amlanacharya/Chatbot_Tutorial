"""
Module 12: Performance Optimization - Streaming Responses

This module demonstrates how to implement streaming responses for chatbots:
1. Basic streaming implementation with Groq API
2. Token-by-token display in the terminal
3. Performance comparison between streaming and non-streaming

Streaming responses improve perceived performance by showing results incrementally
as they're generated, rather than waiting for the complete response.
"""

import os
import time
import json
import requests
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Non-streaming chat function (for comparison)
def chat_without_streaming(prompt, model="llama3-8b-8192"):
    """
    Send a prompt to the Groq API without streaming.
    
    Args:
        prompt (str): The user's message
        model (str): The model to use for generation
        
    Returns:
        dict: The response data including content and timing information
    """
    start_time = time.time()
    
    # API endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Request headers
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Request body
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        # Send request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Calculate time
        end_time = time.time()
        response_time = end_time - start_time
        
        return {
            "content": result["choices"][0]["message"]["content"],
            "response_time": response_time,
            "total_tokens": len(result["choices"][0]["message"]["content"].split())
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "content": f"Error: {str(e)}",
            "response_time": time.time() - start_time,
            "total_tokens": 0
        }

# Streaming chat function
def chat_with_streaming(prompt, model="llama3-8b-8192", display=True):
    """
    Send a prompt to the Groq API with streaming enabled.
    
    Args:
        prompt (str): The user's message
        model (str): The model to use for generation
        display (bool): Whether to display the streaming output
        
    Returns:
        dict: The response data including content and timing information
    """
    start_time = time.time()
    
    # API endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Request headers
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Request body
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": True  # Enable streaming
    }
    
    try:
        # Send request with stream=True to get response chunks
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        # Variables to collect the full response and track tokens
        full_response = ""
        token_count = 0
        first_token_time = None
        
        if display:
            print("\nStreaming response: ", end="", flush=True)
        
        # Process the streaming response
        for line in response.iter_lines():
            if line:
                # Skip empty lines
                line = line.decode('utf-8')
                
                # Skip the "data: " prefix
                if line.startswith("data: "):
                    line = line[6:]
                
                # Skip the "[DONE]" message
                if line == "[DONE]":
                    continue
                
                try:
                    # Parse the JSON data
                    data = json.loads(line)
                    
                    # Extract the content delta
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            content = choice["delta"]["content"]
                            
                            # Record time of first token
                            if token_count == 0:
                                first_token_time = time.time()
                            
                            # Add to full response
                            full_response += content
                            token_count += 1
                            
                            # Display the token if requested
                            if display:
                                print(content, end="", flush=True)
                except json.JSONDecodeError:
                    # Skip invalid JSON
                    continue
        
        # Calculate timing metrics
        end_time = time.time()
        total_time = end_time - start_time
        time_to_first_token = first_token_time - start_time if first_token_time else 0
        
        if display:
            print("\n")  # Add a newline after streaming
        
        return {
            "content": full_response,
            "response_time": total_time,
            "time_to_first_token": time_to_first_token,
            "total_tokens": token_count
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error: {str(e)}"
        if display:
            print(error_msg)
        
        return {
            "content": error_msg,
            "response_time": time.time() - start_time,
            "time_to_first_token": 0,
            "total_tokens": 0
        }

# Demonstration function
def demonstrate_streaming():
    """Demonstrate the difference between streaming and non-streaming responses"""
    print("\n" + "="*80)
    print("CHATBOT PERFORMANCE OPTIMIZATION: STREAMING RESPONSES".center(80))
    print("="*80)
    
    # Create test prompts
    test_prompts = [
        "Write a short paragraph about artificial intelligence.",
        "Explain the benefits of cloud computing in 5 sentences.",
        "List 3 advantages of using Python for data science."
    ]
    
    # Test results
    non_streaming_results = []
    streaming_results = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        
        # Test without streaming
        print("\n1. WITHOUT STREAMING")
        print("-" * 40)
        
        print("Generating response (waiting for full response)...")
        non_streaming_response = chat_without_streaming(prompt)
        
        print(f"Response time: {non_streaming_response['response_time']:.2f} seconds")
        print(f"Response: {non_streaming_response['content']}")
        
        non_streaming_results.append(non_streaming_response)
        
        # Test with streaming
        print("\n2. WITH STREAMING")
        print("-" * 40)
        
        streaming_response = chat_with_streaming(prompt)
        
        print(f"Total response time: {streaming_response['response_time']:.2f} seconds")
        print(f"Time to first token: {streaming_response['time_to_first_token']:.2f} seconds")
        
        streaming_results.append(streaming_response)
    
    # Summary
    print("\n\nPERFORMANCE SUMMARY")
    print("-" * 40)
    
    # Calculate averages
    avg_non_streaming_time = sum(r["response_time"] for r in non_streaming_results) / len(non_streaming_results)
    avg_streaming_total_time = sum(r["response_time"] for r in streaming_results) / len(streaming_results)
    avg_time_to_first_token = sum(r["time_to_first_token"] for r in streaming_results) / len(streaming_results)
    
    print(f"Average response time without streaming: {avg_non_streaming_time:.2f} seconds")
    print(f"Average total time with streaming: {avg_streaming_total_time:.2f} seconds")
    print(f"Average time to first token: {avg_time_to_first_token:.2f} seconds")
    
    # Calculate perceived improvement
    perceived_improvement = ((avg_non_streaming_time - avg_time_to_first_token) / avg_non_streaming_time) * 100
    
    print(f"\nPerceived performance improvement: {perceived_improvement:.2f}%")
    print("(Based on time to first token vs. waiting for complete response)")

# Interactive demo
def interactive_demo():
    """Interactive demo to test streaming vs non-streaming"""
    print("\n" + "="*80)
    print("INTERACTIVE STREAMING DEMO".center(80))
    print("="*80)
    
    while True:
        print("\nEnter a prompt to test streaming (or 'exit' to quit):")
        prompt = input("> ").strip()
        
        if prompt.lower() == 'exit':
            break
        
        # Test both approaches
        print("\nTesting streaming vs. non-streaming...")
        
        # Non-streaming
        print("\n1. WITHOUT STREAMING")
        print("Generating response (waiting for full response)...")
        start = time.time()
        response = chat_without_streaming(prompt)
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content']}")
        
        # Streaming
        print("\n2. WITH STREAMING")
        response = chat_with_streaming(prompt)
        
        print(f"\nTotal response time: {response['response_time']:.2f} seconds")
        print(f"Time to first token: {response['time_to_first_token']:.2f} seconds")
        
        # Calculate perceived improvement
        perceived_improvement = ((response['response_time'] - response['time_to_first_token']) / response['response_time']) * 100
        print(f"Perceived performance improvement: {perceived_improvement:.2f}%")

# Typing effect demo
def typing_effect_demo():
    """Demonstrate how to create a typing effect with streaming"""
    print("\n" + "="*80)
    print("TYPING EFFECT DEMO".center(80))
    print("="*80)
    
    print("\nEnter a prompt to see a typing effect:")
    prompt = input("> ").strip()
    
    print("\nGenerating response with typing effect...")
    
    # Get streaming response but don't display it
    response = chat_with_streaming(prompt, display=False)
    content = response["content"]
    
    # Simulate typing effect
    for char in content:
        print(char, end="", flush=True)
        # Randomize typing speed slightly for more natural effect
        delay = 0.02 + (0.03 * (char in ['.', ',', '!', '?', '\n']))
        time.sleep(delay)
    
    print("\n\nTyping effect complete!")
    print(f"Total tokens: {response['total_tokens']}")
    print(f"Total response time: {response['response_time']:.2f} seconds")
    print(f"Time to first token: {response['time_to_first_token']:.2f} seconds")

if __name__ == "__main__":
    print("Module 12: Performance Optimization - Streaming Responses")
    print("\nThis module demonstrates how to implement streaming responses for chatbots.")
    
    while True:
        print("\nChoose an option:")
        print("1. Run automated demonstration")
        print("2. Interactive demo")
        print("3. Typing effect demo")
        print("4. Exit")
        
        choice = input("> ").strip()
        
        if choice == "1":
            demonstrate_streaming()
        elif choice == "2":
            interactive_demo()
        elif choice == "3":
            typing_effect_demo()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")
