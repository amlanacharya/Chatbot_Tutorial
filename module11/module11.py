"""
Module 11: Advanced Local Model Deployment

This module covers advanced techniques for deploying local models:
1. Managing model formats and quantization
2. Optimizing for CPU/GPU
3. Handling different model architectures
4. Prompt formatting for different models
"""

import os
import torch
import time
import psutil
import platform
import numpy as np
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    BitsAndBytesConfig,
    pipeline
)
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if CUDA is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

def introduction_to_advanced_deployment():
    """
    Print an introduction to advanced model deployment
    """
    print("\n" + "="*80)
    print("ADVANCED LOCAL MODEL DEPLOYMENT".center(80))
    print("="*80)
    
    print("""
As you move beyond basic model loading and inference, advanced deployment requires:

1. 🧩 Understanding model formats and quantization techniques
2. ⚡ Optimizing models for your specific hardware (CPU/GPU)
3. 🔄 Handling different model architectures and their requirements
4. 📝 Mastering prompt formatting for different model families

These techniques allow you to:
- Run larger models on limited hardware
- Improve inference speed
- Reduce memory usage
- Support a wider range of model architectures
    """)
    print("="*80 + "\n")

def explain_model_formats_and_quantization():
    """
    Explain different model formats and quantization techniques
    """
    print("\n" + "="*80)
    print("MODEL FORMATS AND QUANTIZATION".center(80))
    print("="*80)
    
    print("""
MODEL FORMATS:
-------------
1. PyTorch Format (.bin/.pt):
   - Native format for PyTorch models
   - Used by most Hugging Face models
   - Typically larger file size

2. ONNX Format (.onnx):
   - Open Neural Network Exchange format
   - Framework-independent standard
   - Better performance on some hardware
   - Supports deployment on specialized hardware

3. TensorRT Format:
   - NVIDIA's optimized runtime for deep learning
   - Significantly faster inference on NVIDIA GPUs
   - Requires conversion from PyTorch/ONNX

4. GPTQ Format:
   - Post-training quantization method
   - Reduces model size while maintaining quality
   - Popular for consumer-grade GPUs

5. AWQ Format:
   - Activation-aware Weight Quantization
   - Better quality than GPTQ at same bit-width
   - Newer and less widely supported

QUANTIZATION TECHNIQUES:
----------------------
1. FP32 (32-bit floating point):
   - Full precision, largest size
   - Best quality, slowest speed
   - Baseline for comparison

2. FP16 (16-bit floating point):
   - Half precision
   - ~2x smaller than FP32
   - Minimal quality loss, faster inference
   - Standard for GPU inference

3. BF16 (Brain Floating Point):
   - Alternative 16-bit format
   - Better numerical range than FP16
   - Good for training and inference

4. INT8 (8-bit integer):
   - ~4x smaller than FP32
   - Some quality degradation
   - Significantly faster inference

5. INT4 (4-bit integer):
   - ~8x smaller than FP32
   - More noticeable quality impact
   - Fastest inference, smallest size

6. Mixed Precision:
   - Different precision for different layers
   - Optimizes size/quality tradeoff
   - Example: 4-bit for attention, 8-bit for feed-forward
    """)
    print("="*80 + "\n")

def explain_hardware_optimization():
    """
    Explain optimization techniques for different hardware
    """
    print("\n" + "="*80)
    print("OPTIMIZING FOR CPU/GPU".center(80))
    print("="*80)
    
    print("""
CPU OPTIMIZATION:
---------------
1. Thread Optimization:
   - Set appropriate number of threads (typically # of cores)
   - Control with: torch.set_num_threads(n)

2. Memory Mapping:
   - Load large models without full RAM usage
   - Use 'mmap=True' when loading models

3. Quantization:
   - INT8 quantization works well on modern CPUs
   - Use ONNX Runtime for better CPU performance

4. Batch Processing:
   - Process multiple inputs together
   - Increases throughput at cost of latency

5. CPU-Specific Libraries:
   - Intel MKL for Intel CPUs
   - OpenBLAS for AMD CPUs

GPU OPTIMIZATION:
---------------
1. Precision Selection:
   - Use FP16 or BF16 as default
   - Consider INT8/INT4 for consumer GPUs

2. Memory Management:
   - Use gradient checkpointing to reduce memory
   - Implement attention caching for long sequences

3. Batch Size Tuning:
   - Find optimal batch size for your GPU
   - Larger batches = better throughput

4. Flash Attention:
   - Specialized attention implementation
   - Significantly faster and more memory-efficient

5. Tensor Parallelism:
   - Split model across multiple GPUs
   - Useful for very large models

6. KV Cache Management:
   - Optimize key-value cache for generation
   - Prune or compress KV cache for long contexts

HYBRID APPROACHES:
----------------
1. CPU+GPU Offloading:
   - Store parts of model on CPU, parts on GPU
   - Useful for models larger than GPU memory

2. Multi-GPU Strategies:
   - Model parallelism: Split model across GPUs
   - Pipeline parallelism: Split layers across GPUs
   - Data parallelism: Process different batches on different GPUs
    """)
    print("="*80 + "\n")

def explain_model_architectures():
    """
    Explain different model architectures and their requirements
    """
    print("\n" + "="*80)
    print("HANDLING DIFFERENT MODEL ARCHITECTURES".center(80))
    print("="*80)
    
    print("""
COMMON ARCHITECTURES:
-------------------
1. Decoder-Only (GPT-style):
   - Examples: LLaMA, Mistral, GPT-J, Phi
   - Best for text generation
   - Unidirectional attention (can only see past tokens)

2. Encoder-Only (BERT-style):
   - Examples: BERT, RoBERTa, DeBERTa
   - Best for classification, NER, sentiment analysis
   - Bidirectional attention (can see all tokens)

3. Encoder-Decoder (T5-style):
   - Examples: T5, BART, Flan-T5
   - Best for translation, summarization
   - Combines both architectures

ARCHITECTURE-SPECIFIC CONSIDERATIONS:
-----------------------------------
1. Decoder-Only Models:
   - Require careful prompt formatting
   - Need attention masking for generation
   - Often have model-specific chat templates

2. Encoder-Only Models:
   - Typically fixed-length input
   - No generation capability
   - Good for embeddings and classification

3. Encoder-Decoder Models:
   - Need both encoder and decoder components
   - Require special handling for beam search
   - Often task-specific (trained for specific tasks)

SPECIALIZED ARCHITECTURES:
------------------------
1. Mixture of Experts (MoE):
   - Examples: Mixtral, Switch Transformers
   - Larger but more efficient
   - Requires special handling for routing

2. Retrieval-Augmented Models:
   - Examples: REALM, RAG, RETRO
   - Combine generation with retrieval
   - Need document store integration

3. Multi-Modal Models:
   - Examples: LLaVA, CLIP, Flamingo
   - Process text + images/audio
   - Require preprocessing for non-text inputs
    """)
    print("="*80 + "\n")

def explain_prompt_formatting():
    """
    Explain prompt formatting for different model families
    """
    print("\n" + "="*80)
    print("PROMPT FORMATTING FOR DIFFERENT MODELS".center(80))
    print("="*80)
    
    print("""
PROMPT FORMATTING BY MODEL FAMILY:
--------------------------------
1. LLaMA/Llama 2 Format:
   ```
   <s>[INST] <<SYS>>
   {system_prompt}
   <</SYS>>
   
   {user_message} [/INST] {assistant_response} </s>
   ```

2. Mistral Format:
   ```
   <s>[INST] {user_message} [/INST] {assistant_response} </s>
   ```

3. ChatML Format (Claude, some GPT models):
   ```
   <|im_start|>system
   {system_prompt}<|im_end|>
   <|im_start|>user
   {user_message}<|im_end|>
   <|im_start|>assistant
   {assistant_response}<|im_end|>
   ```

4. Vicuna/FastChat Format:
   ```
   USER: {user_message}
   ASSISTANT: {assistant_response}
   ```

5. Alpaca Format:
   ```
   ### Instruction:
   {user_message}
   
   ### Response:
   {assistant_response}
   ```

6. TinyLlama Format:
   ```
   <|user|>
   {user_message}
   <|assistant|>
   {assistant_response}
   ```

7. Gemma Format:
   ```
   <start_of_turn>user
   {user_message}<end_of_turn>
   <start_of_turn>model
   {assistant_response}<end_of_turn>
   ```

HANDLING CHAT HISTORY:
--------------------
For multi-turn conversations, most models expect the entire conversation history
in the prompt. For example, with Llama 2:

```
<s>[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_message_1} [/INST] {assistant_response_1} </s><s>[INST] {user_message_2} [/INST]
```

USING CHAT TEMPLATES:
-------------------
Hugging Face tokenizers often include built-in chat templates:

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},
    {"role": "assistant", "content": ""}
]
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
```

This automatically formats the prompt correctly for the specific model.
    """)
    print("="*80 + "\n")

def load_quantized_model(model_name, quantization_type="4bit"):
    """
    Load a model with specified quantization
    
    Args:
        model_name (str): Name of the model on Hugging Face Hub
        quantization_type (str): Type of quantization to use (4bit, 8bit, none)
        
    Returns:
        tuple: (model, tokenizer)
    """
    print(f"\nLoading model: {model_name} with {quantization_type} quantization")
    print("This may take a few moments depending on your internet connection and the model size...")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Configure quantization
        if quantization_type == "4bit" and DEVICE == "cuda":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",  # normalized float 4
                bnb_4bit_use_double_quant=True
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                quantization_config=quantization_config
            )
            print("Model loaded with 4-bit quantization")
            
        elif quantization_type == "8bit" and DEVICE == "cuda":
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.float16
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                quantization_config=quantization_config
            )
            print("Model loaded with 8-bit quantization")
            
        else:
            # No quantization or CPU
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto" if DEVICE == "cuda" else None,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
            )
            print(f"Model loaded in {'16-bit' if DEVICE == 'cuda' else '32-bit'} precision")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None, None

def benchmark_inference(model, tokenizer, prompt, num_runs=3):
    """
    Benchmark inference speed and memory usage
    
    Args:
        model: The loaded model
        tokenizer: The loaded tokenizer
        prompt (str): The input prompt
        num_runs (int): Number of runs for averaging
        
    Returns:
        dict: Benchmark results
    """
    if model is None or tokenizer is None:
        return {"error": "Model or tokenizer not loaded correctly."}
    
    try:
        # Prepare input
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Warm-up run
        with torch.no_grad():
            _ = model.generate(
                inputs["input_ids"],
                max_new_tokens=20,
                do_sample=False
            )
        
        # Measure memory before
        if DEVICE == "cuda":
            torch.cuda.synchronize()
            mem_before = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
        else:
            mem_before = psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)  # MB
        
        # Benchmark runs
        latencies = []
        for _ in range(num_runs):
            # Time generation
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    inputs["input_ids"],
                    max_new_tokens=50,
                    do_sample=False
                )
            if DEVICE == "cuda":
                torch.cuda.synchronize()
            end_time = time.time()
            
            latencies.append(end_time - start_time)
        
        # Measure memory after
        if DEVICE == "cuda":
            torch.cuda.synchronize()
            mem_after = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
        else:
            mem_after = psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)  # MB
        
        # Calculate metrics
        avg_latency = sum(latencies) / len(latencies)
        tokens_per_second = 50 / avg_latency
        memory_used = mem_after - mem_before
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "avg_latency_seconds": avg_latency,
            "tokens_per_second": tokens_per_second,
            "memory_used_mb": memory_used,
            "generated_text": generated_text,
            "latencies": latencies
        }
        
    except Exception as e:
        return {"error": f"Error during benchmark: {str(e)}"}

def format_prompt_for_model(model_name, user_message, system_prompt="You are a helpful AI assistant."):
    """
    Format a prompt according to the model's expected format
    
    Args:
        model_name (str): Name or family of the model
        user_message (str): User's input message
        system_prompt (str): System instructions
        
    Returns:
        str: Formatted prompt
    """
    model_name = model_name.lower()
    
    # LLaMA 2 family
    if "llama-2" in model_name or "llama2" in model_name:
        return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_message} [/INST] "
    
    # Mistral family
    elif "mistral" in model_name:
        return f"<s>[INST] {user_message} [/INST] "
    
    # ChatML format (Claude-like)
    elif "claude" in model_name or "gpt" in model_name:
        return f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"
    
    # Vicuna/FastChat format
    elif "vicuna" in model_name or "fastchat" in model_name:
        return f"USER: {user_message}\nASSISTANT: "
    
    # Alpaca format
    elif "alpaca" in model_name:
        return f"### Instruction:\n{user_message}\n\n### Response:\n"
    
    # TinyLlama format
    elif "tinyllama" in model_name:
        return f"<|user|>\n{user_message}\n<|assistant|>\n"
    
    # Gemma format
    elif "gemma" in model_name:
        return f"<start_of_turn>user\n{user_message}<end_of_turn>\n<start_of_turn>model\n"
    
    # Default format (simple)
    else:
        return f"{system_prompt}\n\nUser: {user_message}\nAssistant: "

def create_gradio_interface():
    """
    Create a Gradio interface for model benchmarking and comparison
    """
    # Available models to choose from
    model_options = [
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Very small model (1.1B parameters)
        "microsoft/phi-2",                      # Small model (2.7B parameters)
        "google/gemma-2b-it",                   # Small model (2B parameters)
        "mistralai/Mistral-7B-Instruct-v0.2",   # Medium model (7B parameters)
        "meta-llama/Llama-2-7b-chat-hf"         # Medium model (7B parameters)
    ]
    
    # Quantization options
    quantization_options = ["4bit", "8bit", "none"]
    
    # Global variables to store the loaded models and tokenizers
    loaded_models = {}
    
    def load_and_benchmark(model_name, quantization, prompt, num_runs):
        """Load model and run benchmark"""
        model_key = f"{model_name}_{quantization}"
        
        # Load model if not already loaded
        if model_key not in loaded_models:
            model, tokenizer = load_quantized_model(model_name, quantization)
            if model is not None and tokenizer is not None:
                loaded_models[model_key] = {"model": model, "tokenizer": tokenizer}
            else:
                return f"Failed to load {model_name} with {quantization} quantization."
        
        # Get model and tokenizer
        model = loaded_models[model_key]["model"]
        tokenizer = loaded_models[model_key]["tokenizer"]
        
        # Format prompt for the specific model
        formatted_prompt = format_prompt_for_model(model_name, prompt)
        
        # Run benchmark
        results = benchmark_inference(model, tokenizer, formatted_prompt, num_runs=int(num_runs))
        
        if "error" in results:
            return results["error"]
        
        # Format results
        output = f"### Benchmark Results for {model_name} ({quantization})\n\n"
        output += f"**Average Latency:** {results['avg_latency_seconds']:.4f} seconds\n"
        output += f"**Tokens Per Second:** {results['tokens_per_second']:.2f}\n"
        output += f"**Memory Used:** {results['memory_used_mb']:.2f} MB\n\n"
        output += f"**Generated Text:**\n{results['generated_text']}\n\n"
        output += f"**Individual Latencies:** {[round(lat, 4) for lat in results['latencies']]}"
        
        return output
    
    def compare_models(model1, quant1, model2, quant2, prompt, num_runs):
        """Compare two models with different quantization"""
        result1 = load_and_benchmark(model1, quant1, prompt, num_runs)
        result2 = load_and_benchmark(model2, quant2, prompt, num_runs)
        
        return f"## Model 1: {model1} ({quant1})\n\n{result1}\n\n## Model 2: {model2} ({quant2})\n\n{result2}"
    
    def get_system_info():
        """Get system information"""
        info = "### System Information\n\n"
        
        # CPU info
        info += f"**CPU:** {platform.processor()}\n"
        info += f"**Cores:** {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical\n"
        
        # RAM info
        ram = psutil.virtual_memory()
        info += f"**RAM:** {ram.total / (1024**3):.2f} GB total, {ram.available / (1024**3):.2f} GB available\n"
        
        # GPU info if available
        if torch.cuda.is_available():
            info += f"**GPU:** {torch.cuda.get_device_name(0)}\n"
            info += f"**CUDA Version:** {torch.version.cuda}\n"
            info += f"**GPU Memory:** {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB\n"
        else:
            info += "**GPU:** Not available\n"
        
        # Python and library versions
        info += f"**Python Version:** {platform.python_version()}\n"
        info += f"**PyTorch Version:** {torch.__version__}\n"
        
        return info
    
    # Create interface
    with gr.Blocks(title="Advanced Model Deployment Benchmark") as demo:
        gr.Markdown("# Advanced Model Deployment and Benchmarking")
        
        with gr.Tab("System Information"):
            gr.Markdown(get_system_info())
        
        with gr.Tab("Single Model Benchmark"):
            with gr.Row():
                model_dropdown = gr.Dropdown(choices=model_options, label="Select Model", value=model_options[0])
                quant_dropdown = gr.Dropdown(choices=quantization_options, label="Quantization", value="4bit")
            
            prompt_input = gr.Textbox(label="Prompt", value="Explain quantum computing in simple terms.")
            num_runs = gr.Slider(minimum=1, maximum=10, value=3, step=1, label="Number of Benchmark Runs")
            
            benchmark_button = gr.Button("Run Benchmark")
            result_output = gr.Markdown(label="Benchmark Results")
            
            benchmark_button.click(
                load_and_benchmark,
                inputs=[model_dropdown, quant_dropdown, prompt_input, num_runs],
                outputs=result_output
            )
        
        with gr.Tab("Model Comparison"):
            with gr.Row():
                with gr.Column():
                    model1_dropdown = gr.Dropdown(choices=model_options, label="Model 1", value=model_options[0])
                    quant1_dropdown = gr.Dropdown(choices=quantization_options, label="Quantization 1", value="4bit")
                
                with gr.Column():
                    model2_dropdown = gr.Dropdown(choices=model_options, label="Model 2", value=model_options[1])
                    quant2_dropdown = gr.Dropdown(choices=quantization_options, label="Quantization 2", value="4bit")
            
            compare_prompt = gr.Textbox(label="Prompt", value="Explain quantum computing in simple terms.")
            compare_runs = gr.Slider(minimum=1, maximum=10, value=3, step=1, label="Number of Benchmark Runs")
            
            compare_button = gr.Button("Compare Models")
            compare_output = gr.Markdown(label="Comparison Results")
            
            compare_button.click(
                compare_models,
                inputs=[model1_dropdown, quant1_dropdown, model2_dropdown, quant2_dropdown, compare_prompt, compare_runs],
                outputs=compare_output
            )
    
    return demo

def main():
    """Main function to demonstrate advanced model deployment techniques"""
    
    # Print introduction
    introduction_to_advanced_deployment()
    
    # Explain model formats and quantization
    explain_model_formats_and_quantization()
    
    # Explain hardware optimization
    explain_hardware_optimization()
    
    # Explain model architectures
    explain_model_architectures()
    
    # Explain prompt formatting
    explain_prompt_formatting()
    
    # Ask user if they want to launch the benchmark interface
    print("\nWould you like to launch the model benchmarking interface? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        # Create and launch the Gradio interface
        demo = create_gradio_interface()
        print("\nLaunching Gradio interface for model benchmarking...")
        demo.launch()
    else:
        print("\nSkipping benchmark interface.")
        print("You can run this module again later to benchmark models.")

if __name__ == "__main__":
    main()
