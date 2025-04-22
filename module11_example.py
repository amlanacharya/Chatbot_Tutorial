"""
Module 11 Example: Comparing quantization techniques

This example demonstrates how to:
1. Load the same model with different quantization settings
2. Compare inference speed and memory usage
3. Format prompts correctly for the model
4. Visualize the performance differences
"""

import torch
import time
import matplotlib.pyplot as plt
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

def main():
    # Define model name - using a small model for quick demonstration
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    print(f"Comparing quantization techniques for {model_name}")
    
    # Test prompt
    prompt = "Explain the benefits of model quantization in simple terms."
    
    # Format prompt for TinyLlama
    formatted_prompt = f"<|user|>\n{prompt}\n<|assistant|>\n"
    
    # Load tokenizer (shared across all model variants)
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Define quantization configurations to test
    configs = []
    
    # Only add CUDA configurations if GPU is available
    if torch.cuda.is_available():
        # FP16 (no quantization)
        configs.append({
            "name": "FP16",
            "load_params": {
                "torch_dtype": torch.float16,
                "device_map": "auto"
            }
        })
        
        # 8-bit quantization
        configs.append({
            "name": "INT8",
            "load_params": {
                "device_map": "auto",
                "quantization_config": BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_8bit_compute_dtype=torch.float16
                )
            }
        })
        
        # 4-bit quantization
        configs.append({
            "name": "INT4",
            "load_params": {
                "device_map": "auto",
                "quantization_config": BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
            }
        })
    else:
        # CPU only - FP32
        configs.append({
            "name": "FP32 (CPU)",
            "load_params": {
                "torch_dtype": torch.float32
            }
        })
    
    # Results storage
    results = []
    
    # Test each configuration
    for config in configs:
        print(f"\nLoading model with {config['name']} configuration...")
        
        # Measure loading time and memory
        load_start = time.time()
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **config["load_params"]
        )
        
        load_time = time.time() - load_start
        
        # Prepare input
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        # Warm-up run
        with torch.no_grad():
            _ = model.generate(
                inputs["input_ids"],
                max_new_tokens=20,
                do_sample=False
            )
        
        # Measure inference time
        inference_start = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        
        inference_time = time.time() - inference_start
        
        # Get memory usage
        if torch.cuda.is_available():
            memory_usage = torch.cuda.max_memory_allocated() / (1024 ** 3)  # GB
        else:
            memory_usage = 0  # Not tracking CPU memory
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        if "<|assistant|>" in formatted_prompt:
            response = generated_text.split("<|assistant|>")[-1].strip()
        else:
            response = generated_text.replace(formatted_prompt, "").strip()
        
        # Store results
        results.append({
            "config": config["name"],
            "load_time": load_time,
            "inference_time": inference_time,
            "memory_usage": memory_usage,
            "response": response
        })
        
        # Print results
        print(f"\nResults for {config['name']}:")
        print(f"  Load time: {load_time:.2f} seconds")
        print(f"  Inference time: {inference_time:.2f} seconds")
        print(f"  Memory usage: {memory_usage:.2f} GB")
        print(f"  Response: {response[:100]}...")
        
        # Free up memory
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    # Visualize results if we have multiple configurations
    if len(results) > 1:
        visualize_results(results)

def visualize_results(results):
    """Create visualizations comparing the different quantization methods"""
    
    # Extract data for plotting
    configs = [r["config"] for r in results]
    load_times = [r["load_time"] for r in results]
    inference_times = [r["inference_time"] for r in results]
    memory_usages = [r["memory_usage"] for r in results]
    
    # Create figure with subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot load times
    ax1.bar(configs, load_times, color='blue')
    ax1.set_title('Model Load Time (s)')
    ax1.set_ylabel('Seconds')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot inference times
    ax2.bar(configs, inference_times, color='green')
    ax2.set_title('Inference Time (s)')
    ax2.set_ylabel('Seconds')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot memory usage
    ax3.bar(configs, memory_usages, color='red')
    ax3.set_title('Memory Usage (GB)')
    ax3.set_ylabel('GB')
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('quantization_comparison.png')
    print("\nVisualization saved as 'quantization_comparison.png'")
    
    # Show plot if running in interactive environment
    try:
        plt.show()
    except:
        pass

if __name__ == "__main__":
    main()
