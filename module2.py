import requests
import os
from dotenv import load_dotenv


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

class GroqChatbot:
    def __init__(self, api_key, model="llama3-70b-8192"):
        """
        Initialize the chatbot with API key and model.
        
        Args:
            api_key (str): The Groq API key
            model (str): The model to use for generation
        """
        self.api_key = api_key
        self.model = model
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, message):
        """
        Send a message to the chatbot and get a response.
        
        Args:
            message (str): The user's message
            
        Returns:
            str: The generated response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare request body
        data = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            
            response = requests.post(self.url, headers=self.headers, json=data)
            
            response.raise_for_status()
            
            result = response.json()
            
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Add assistant response to history-The extra step
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def clear_history(self):
        """Reset the conversation history, keeping only the system message."""
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        return "Conversation history cleared."
    
    def change_model(self, new_model):
        """Change the model used for generation."""
        self.model = new_model
        return f"Model changed to {new_model}."
    
    def display_history(self):
        """Display the conversation history."""
        history = ""
        for message in self.conversation_history:
            if message["role"] != "system":
                role = "You" if message["role"] == "user" else "AI"
                history += f"{role}: {message['content']}\n\n"
        return history

def main():
    """Run the chatbot in a command-line interface."""
    print("Initializing Groq Chatbot...")
    chatbot = GroqChatbot(GROQ_API_KEY)
    print("Chatbot initialized successfully!")
    print("\nWelcome to the Groq Chatbot!")
    print("Type 'exit' to quit, 'clear' to clear conversation history, 'history' to view conversation history.")
    print("Type 'model:model_name' to change the model (e.g., 'model:llama3-8b-8192').")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        # Check for special commands
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'clear':
            print(chatbot.clear_history())
            continue
        elif user_input.lower() == 'history':
            print("\nConversation History:")
            print(chatbot.display_history())
            continue
        elif user_input.lower().startswith('model:'):
            new_model = user_input[6:].strip()
            print(chatbot.change_model(new_model))
            continue
        
        # Get response from chatbot
        print("\nAI is thinking...")
        response = chatbot.send_message(user_input)
        print(f"\nAI: {response}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")