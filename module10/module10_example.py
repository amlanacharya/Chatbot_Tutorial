"""
Module 10 Example: Using a small local model for text generation

This example demonstrates how to:
1. Load a small language model (TinyLlama)
2. Generate text with the model
3. Control generation parameters
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def main():
    # Define model name
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    print(f"Loading {model_name}...")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    
    print("Model loaded successfully!")
    
    # Example prompts
    prompts = [
        "What are the main features of Python?",
        "Write a short poem about artificial intelligence.",
        "Explain quantum computing to a 10-year-old."
    ]
    
    # Generation parameters to experiment with
    parameters = [
        {"temperature": 0.7, "max_length": 256, "do_sample": True},
        {"temperature": 1.2, "max_length": 256, "do_sample": True},
        {"temperature": 0.1, "max_length": 256, "do_sample": True}
    ]
    
    # Format for TinyLlama chat model
    def format_prompt(text):
        return f"<|user|>\n{text}\n<|assistant|>\n"
    
    # Generate responses for each prompt with different parameters
    for i, prompt in enumerate(prompts):
        print(f"\n\n{'='*80}")
        print(f"PROMPT {i+1}: {prompt}")
        print(f"{'='*80}")
        
        formatted_prompt = format_prompt(prompt)
        
        for j, params in enumerate(parameters):
            print(f"\n--- Generation with temperature={params['temperature']} ---")
            
            # Tokenize input
            inputs = tokenizer(formatted_prompt, return_tensors="pt")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate text
            with torch.no_grad():
                outputs = model.generate(
                    inputs["input_ids"],
                    max_length=params["max_length"],
                    temperature=params["temperature"],
                    do_sample=params["do_sample"],
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            response = generated_text.split("<|assistant|>")[-1].strip()
            
            print(f"Response: {response}")
            print(f"Token count: {len(outputs[0])}")
    
    print("\n\nExample completed! You've seen how different parameters affect text generation.")

if __name__ == "__main__":
    main()
