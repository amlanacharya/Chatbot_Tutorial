import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:#incase you dnt have api_key
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

def chat_with_groq(prompt, model="llama3-70b-8192"):
    """
    Send a prompt to the Groq API and get a response.
    
    Args:
        prompt (str): The user's message
        model (str): The model to use for generation
        
    Returns:
        str: The generated response
    """
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
        "max_tokens": 1024
    }
    
    try:
        # Send via post method
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response in json format
        result = response.json()
        
        # add # after choices and result and test the various repsonse
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    user_prompt = "Explain quantum computing in simple terms."
    print(f"Sending prompt: {user_prompt}")
    
    response = chat_with_groq(user_prompt)
    print("\nResponse from Groq API:")
    print(response)