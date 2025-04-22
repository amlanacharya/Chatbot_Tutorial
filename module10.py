"""
Module 10: Introduction to Hugging Face Transformers

This module introduces Hugging Face's ecosystem and demonstrates how to:
1. Set up the environment for local models
2. Load your first model
3. Perform basic inference
4. Create a simple interface for interacting with local models
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if CUDA is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

def introduction_to_huggingface():
    """
    Print an introduction to Hugging Face's ecosystem
    """
    print("\n" + "="*80)
    print("INTRODUCTION TO HUGGING FACE TRANSFORMERS".center(80))
    print("="*80)
    
    print("""
Hugging Face is an AI community and platform that provides:

1. 🤗 Model Hub: A repository of pre-trained models (100,000+) for NLP, computer vision, 
   audio processing, and more.

2. 🔧 Transformers Library: A Python library that provides APIs and tools to easily 
   download and train state-of-the-art pretrained models.

3. 📚 Datasets: A library and platform for easily sharing and accessing datasets.

4. 🧪 Spaces: A platform for hosting ML demo apps.

5. 🧠 AutoTrain: Tools for training models without writing code.

Key advantages of using Hugging Face for local models:
- Run models on your own hardware without API costs
- Full control over model parameters and behavior
- Privacy - data doesn't leave your machine
- Ability to fine-tune models for specific use cases
- No internet connection required for inference
    """)
    print("="*80 + "\n")

def setup_environment():
    """
    Guide for setting up the environment for local models
    """
    print("\n" + "="*80)
    print("SETTING UP THE ENVIRONMENT".center(80))
    print("="*80)
    
    print("""
To use Hugging Face Transformers locally, you need:

1. Python 3.7+ environment
2. PyTorch or TensorFlow installed
3. transformers library: pip install transformers
4. For text generation: pip install accelerate
5. For better performance: pip install sentencepiece protobuf
6. For quantized models: pip install bitsandbytes

Hardware considerations:
- CPU: Works for smaller models but slow
- GPU: Recommended for faster inference (CUDA for NVIDIA GPUs)
- RAM: 8GB+ for small models, 16GB+ for medium models
- VRAM: 4GB+ for quantized models, 8GB+ for medium models, 24GB+ for large models

Model size categories:
- Small: 125M-1B parameters (e.g., DistilGPT2, TinyLlama)
- Medium: 1B-7B parameters (e.g., Phi-2, Gemma-2B)
- Large: 7B+ parameters (e.g., Llama-2-7B, Mistral-7B)
- XL: 13B+ parameters (e.g., Llama-2-13B)
- XXL: 70B+ parameters (e.g., Llama-2-70B)
    """)
    print("="*80 + "\n")

def load_model(model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0", use_4bit=True):
    """
    Load a model from Hugging Face Hub
    
    Args:
        model_name (str): Name of the model on Hugging Face Hub
        use_4bit (bool): Whether to use 4-bit quantization (reduces memory usage)
        
    Returns:
        tuple: (model, tokenizer)
    """
    print(f"\nLoading model: {model_name}")
    print("This may take a few moments depending on your internet connection and the model size...")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model with quantization if requested
        if use_4bit and DEVICE == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                load_in_4bit=True
            )
            print("Model loaded with 4-bit quantization")
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto" if DEVICE == "cuda" else None,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
            )
            print(f"Model loaded in {'16-bit' if DEVICE == 'cuda' else '32-bit'} precision")
        
        return model, tokenizer
    
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the model name is correct")
        print("3. Try a smaller model if you're running out of memory")
        print("4. Make sure you have the latest transformers library")
        return None, None

def basic_inference(model, tokenizer, prompt, max_length=512, temperature=0.7):
    """
    Perform basic inference with a loaded model
    
    Args:
        model: The loaded model
        tokenizer: The loaded tokenizer
        prompt (str): The input prompt
        max_length (int): Maximum length of generated text
        temperature (float): Controls randomness (higher = more random)
        
    Returns:
        str: Generated text
    """
    if model is None or tokenizer is None:
        return "Model or tokenizer not loaded correctly."
    
    try:
        # Format the prompt based on model type
        if "llama" in model.config.architectures[0].lower():
            # Format for Llama models
            formatted_prompt = f"<|user|>\n{prompt}\n<|assistant|>\n"
        elif "mistral" in model.config.architectures[0].lower():
            # Format for Mistral models
            formatted_prompt = f"[INST] {prompt} [/INST]"
        elif "phi" in model.config.architectures[0].lower():
            # Format for Phi models
            formatted_prompt = f"User: {prompt}\nAssistant:"
        else:
            # Default format
            formatted_prompt = prompt
        
        # Tokenize the prompt
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        
        # Move inputs to the appropriate device
        if DEVICE == "cuda":
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode the generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        if "<|assistant|>" in formatted_prompt:
            response = generated_text.split("<|assistant|>")[-1].strip()
        elif "[/INST]" in formatted_prompt:
            response = generated_text.split("[/INST]")[-1].strip()
        elif "Assistant:" in generated_text:
            response = generated_text.split("Assistant:")[-1].strip()
        else:
            response = generated_text.replace(prompt, "").strip()
        
        return response
    
    except Exception as e:
        return f"Error during inference: {str(e)}"

def create_gradio_interface():
    """
    Create a Gradio interface for interacting with the model
    """
    # Available models to choose from
    model_options = [
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Very small model (1.1B parameters)
        "microsoft/phi-2",                      # Small model (2.7B parameters)
        "google/gemma-2b-it",                   # Small model (2B parameters)
        "mistralai/Mistral-7B-Instruct-v0.2",   # Medium model (7B parameters)
        "meta-llama/Llama-2-7b-chat-hf"         # Medium model (7B parameters)
    ]
    
    # Global variables to store the loaded model and tokenizer
    current_model = {"model": None, "tokenizer": None, "name": None}
    
    def load_selected_model(model_name, use_4bit):
        """Load the selected model and return status"""
        if current_model["name"] == model_name:
            return f"Model {model_name} is already loaded."
        
        model, tokenizer = load_model(model_name, use_4bit)
        
        if model is not None and tokenizer is not None:
            current_model["model"] = model
            current_model["tokenizer"] = tokenizer
            current_model["name"] = model_name
            return f"Successfully loaded {model_name}"
        else:
            return "Failed to load model. Check the console for details."
    
    def generate_response(prompt, max_length, temperature):
        """Generate a response using the loaded model"""
        if current_model["model"] is None or current_model["tokenizer"] is None:
            return "Please load a model first."
        
        return basic_inference(
            current_model["model"], 
            current_model["tokenizer"], 
            prompt, 
            max_length=max_length, 
            temperature=temperature
        )
    
    # Create the Gradio interface
    with gr.Blocks(title="Local LLM Demo") as demo:
        gr.Markdown("# 🤗 Local LLM Demo with Hugging Face Transformers")
        gr.Markdown("Run language models directly on your computer without API calls!")
        
        with gr.Tab("Model Selection"):
            with gr.Row():
                with gr.Column():
                    model_dropdown = gr.Dropdown(
                        model_options, 
                        label="Select Model", 
                        value=model_options[0],
                        info="Smaller models load faster but may produce lower quality outputs"
                    )
                    use_4bit = gr.Checkbox(
                        label="Use 4-bit Quantization", 
                        value=True,
                        info="Reduces memory usage but may slightly reduce quality"
                    )
                    load_button = gr.Button("Load Model")
                with gr.Column():
                    load_status = gr.Textbox(label="Load Status", interactive=False)
        
        with gr.Tab("Chat"):
            with gr.Row():
                with gr.Column():
                    prompt_input = gr.Textbox(
                        label="Your Message", 
                        placeholder="Enter your message here...",
                        lines=4
                    )
                    max_length = gr.Slider(
                        minimum=64, 
                        maximum=2048, 
                        value=512, 
                        step=64, 
                        label="Maximum Length"
                    )
                    temperature = gr.Slider(
                        minimum=0.1, 
                        maximum=1.5, 
                        value=0.7, 
                        step=0.1, 
                        label="Temperature"
                    )
                    generate_button = gr.Button("Generate Response")
                with gr.Column():
                    response_output = gr.Textbox(
                        label="Model Response", 
                        interactive=False,
                        lines=12
                    )
        
        # Set up event handlers
        load_button.click(
            load_selected_model, 
            inputs=[model_dropdown, use_4bit], 
            outputs=load_status
        )
        
        generate_button.click(
            generate_response, 
            inputs=[prompt_input, max_length, temperature], 
            outputs=response_output
        )
    
    return demo

def compare_local_vs_api():
    """
    Print a comparison between local models and API-based models
    """
    print("\n" + "="*80)
    print("LOCAL MODELS VS. API-BASED MODELS".center(80))
    print("="*80)
    
    print("""
┌─────────────────────┬─────────────────────────┬─────────────────────────┐
│                     │ Local Models             │ API-Based Models        │
├─────────────────────┼─────────────────────────┼─────────────────────────┤
│ Cost                │ One-time hardware cost   │ Pay per token/request   │
│ Privacy             │ Data stays on device     │ Data sent to servers    │
│ Setup Complexity    │ Higher                   │ Lower                   │
│ Maintenance         │ Manual updates needed    │ Automatic updates       │
│ Performance         │ Depends on hardware      │ Consistent              │
│ Customization       │ Full control             │ Limited by API          │
│ Scaling             │ Limited by hardware      │ Easy to scale           │
│ Offline Usage       │ Yes                      │ No                      │
│ Model Size Options  │ Limited by hardware      │ Wide range available    │
│ Latency             │ Lower (no network)       │ Higher (network delay)  │
└─────────────────────┴─────────────────────────┴─────────────────────────┘

When to use local models:
- Privacy-sensitive applications
- Offline environments
- Cost-sensitive long-running applications
- When you need full control over the model

When to use API-based models:
- Quick prototyping
- Limited local hardware
- Need for state-of-the-art large models
- Simplicity is prioritized over customization
    """)
    print("="*80 + "\n")

def main():
    """Main function to demonstrate Hugging Face capabilities"""
    
    # Print introduction
    introduction_to_huggingface()
    
    # Print environment setup guide
    setup_environment()
    
    # Compare local models vs API-based models
    compare_local_vs_api()
    
    # Ask user if they want to load a model
    print("\nWould you like to load a local model and start the demo interface? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        # Create and launch the Gradio interface
        demo = create_gradio_interface()
        print("\nLaunching Gradio interface...")
        demo.launch()
    else:
        print("\nSkipping model loading and demo interface.")
        print("You can run this module again later to load models and try the interface.")
    
    print("\nModule 10 completed! You've learned about Hugging Face's ecosystem and how to use local models.")

if __name__ == "__main__":
    main()
