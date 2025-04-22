"""
Module 12: Performance Optimization - Asynchronous Processing

This module demonstrates how to implement asynchronous processing for chatbots:
1. Basic synchronous processing (for comparison)
2. Asynchronous processing with asyncio and aiohttp
3. Handling multiple requests concurrently
4. Performance comparison between sync and async approaches

Asynchronous processing improves throughput by handling multiple requests
concurrently without blocking, which is especially useful for high-traffic applications.
"""

import os
import time
import json
import asyncio
import aiohttp
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Synchronous chat function (for comparison)
def chat_sync(prompt, model="llama3-8b-8192"):
    """
    Send a prompt to the Groq API synchronously.
    
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
        "max_tokens": 150  # Smaller for faster responses in demo
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
            "prompt": prompt,
            "content": result["choices"][0]["message"]["content"],
            "response_time": response_time
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "prompt": prompt,
            "content": f"Error: {str(e)}",
            "response_time": time.time() - start_time
        }

# Asynchronous chat function
async def chat_async(prompt, model="llama3-8b-8192", session=None):
    """
    Send a prompt to the Groq API asynchronously.
    
    Args:
        prompt (str): The user's message
        model (str): The model to use for generation
        session (aiohttp.ClientSession, optional): Existing aiohttp session
        
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
        "max_tokens": 150  # Smaller for faster responses in demo
    }
    
    # Create a session if not provided
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        # Send request asynchronously
        async with session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()
            result = await response.json()
            
            # Calculate time
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "prompt": prompt,
                "content": result["choices"][0]["message"]["content"],
                "response_time": response_time
            }
            
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return {
            "prompt": prompt,
            "content": f"Error: {str(e)}",
            "response_time": time.time() - start_time
        }
    finally:
        # Close the session if we created it
        if close_session:
            await session.close()

# Process multiple prompts synchronously
def process_prompts_sync(prompts, model="llama3-8b-8192"):
    """
    Process multiple prompts synchronously.
    
    Args:
        prompts (list): List of prompts to process
        model (str): The model to use for generation
        
    Returns:
        tuple: (results, total_time)
    """
    start_time = time.time()
    results = []
    
    for prompt in prompts:
        result = chat_sync(prompt, model)
        results.append(result)
        
    total_time = time.time() - start_time
    return results, total_time

# Process multiple prompts asynchronously
async def process_prompts_async(prompts, model="llama3-8b-8192"):
    """
    Process multiple prompts asynchronously.
    
    Args:
        prompts (list): List of prompts to process
        model (str): The model to use for generation
        
    Returns:
        tuple: (results, total_time)
    """
    start_time = time.time()
    
    # Create a shared session for all requests
    async with aiohttp.ClientSession() as session:
        # Create tasks for all prompts
        tasks = [chat_async(prompt, model, session) for prompt in prompts]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_time
    return results, total_time

# Demonstration function
def demonstrate_async():
    """Demonstrate the difference between synchronous and asynchronous processing"""
    print("\n" + "="*80)
    print("CHATBOT PERFORMANCE OPTIMIZATION: ASYNCHRONOUS PROCESSING".center(80))
    print("="*80)
    
    # Create test prompts
    test_prompts = [
        "What is artificial intelligence?",
        "Explain machine learning in one paragraph.",
        "What is deep learning?",
        "How does natural language processing work?",
        "What are neural networks?"
    ]
    
    # Test synchronous processing
    print("\n1. SYNCHRONOUS PROCESSING")
    print("-" * 40)
    
    print(f"Processing {len(test_prompts)} prompts synchronously...")
    sync_results, sync_total_time = process_prompts_sync(test_prompts)
    
    print(f"\nTotal time for synchronous processing: {sync_total_time:.2f} seconds")
    for i, result in enumerate(sync_results):
        print(f"\nPrompt {i+1}: {result['prompt']}")
        print(f"Response time: {result['response_time']:.2f} seconds")
        print(f"Response: {result['content'][:100]}...")
    
    # Test asynchronous processing
    print("\n\n2. ASYNCHRONOUS PROCESSING")
    print("-" * 40)
    
    print(f"Processing {len(test_prompts)} prompts asynchronously...")
    
    # Run the async function in the event loop
    async_results, async_total_time = asyncio.run(process_prompts_async(test_prompts))
    
    print(f"\nTotal time for asynchronous processing: {async_total_time:.2f} seconds")
    for i, result in enumerate(async_results):
        print(f"\nPrompt {i+1}: {result['prompt']}")
        print(f"Response time: {result['response_time']:.2f} seconds")
        print(f"Response: {result['content'][:100]}...")
    
    # Summary
    print("\n\nPERFORMANCE SUMMARY")
    print("-" * 40)
    
    print(f"Total time for synchronous processing: {sync_total_time:.2f} seconds")
    print(f"Total time for asynchronous processing: {async_total_time:.2f} seconds")
    
    # Calculate improvement
    improvement = ((sync_total_time - async_total_time) / sync_total_time) * 100
    print(f"\nPerformance improvement with async: {improvement:.2f}%")
    
    # Calculate average response times
    avg_sync_time = sum(r["response_time"] for r in sync_results) / len(sync_results)
    avg_async_time = sum(r["response_time"] for r in async_results) / len(async_results)
    
    print(f"Average response time (sync): {avg_sync_time:.2f} seconds")
    print(f"Average response time (async): {avg_async_time:.2f} seconds")
    
    # Calculate throughput
    sync_throughput = len(test_prompts) / sync_total_time
    async_throughput = len(test_prompts) / async_total_time
    
    print(f"Throughput (sync): {sync_throughput:.2f} requests/second")
    print(f"Throughput (async): {async_throughput:.2f} requests/second")
    print(f"Throughput improvement: {(async_throughput/sync_throughput - 1) * 100:.2f}%")

# Interactive demo
def interactive_async_demo():
    """Interactive demo to test async processing with custom prompts"""
    print("\n" + "="*80)
    print("INTERACTIVE ASYNC PROCESSING DEMO".center(80))
    print("="*80)
    
    # Get number of prompts
    while True:
        try:
            num_prompts = int(input("\nEnter number of prompts to process (2-10): "))
            if 2 <= num_prompts <= 10:
                break
            print("Please enter a number between 2 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get prompts
    prompts = []
    for i in range(num_prompts):
        prompt = input(f"\nEnter prompt {i+1}: ")
        prompts.append(prompt)
    
    # Process synchronously
    print("\n1. SYNCHRONOUS PROCESSING")
    print("-" * 40)
    
    print(f"Processing {len(prompts)} prompts synchronously...")
    sync_results, sync_total_time = process_prompts_sync(prompts)
    
    print(f"\nTotal time for synchronous processing: {sync_total_time:.2f} seconds")
    
    # Process asynchronously
    print("\n2. ASYNCHRONOUS PROCESSING")
    print("-" * 40)
    
    print(f"Processing {len(prompts)} prompts asynchronously...")
    async_results, async_total_time = asyncio.run(process_prompts_async(prompts))
    
    print(f"\nTotal time for asynchronous processing: {async_total_time:.2f} seconds")
    
    # Show results
    print("\nRESULTS:")
    print("-" * 40)
    
    for i, (sync_result, async_result) in enumerate(zip(sync_results, async_results)):
        print(f"\nPrompt {i+1}: {sync_result['prompt']}")
        print(f"Sync response time: {sync_result['response_time']:.2f} seconds")
        print(f"Async response time: {async_result['response_time']:.2f} seconds")
        print(f"Sync response: {sync_result['content'][:100]}...")
        print(f"Async response: {async_result['content'][:100]}...")
    
    # Summary
    improvement = ((sync_total_time - async_total_time) / sync_total_time) * 100
    print(f"\nPerformance improvement with async: {improvement:.2f}%")

# Batch processing demo
async def batch_processing_demo():
    """Demonstrate batch processing with async"""
    print("\n" + "="*80)
    print("BATCH PROCESSING DEMO".center(80))
    print("="*80)
    
    # Create a large batch of prompts
    batch_size = 10
    print(f"\nGenerating a batch of {batch_size} similar prompts...")
    
    topics = ["Python", "JavaScript", "Java", "C++", "Ruby", "Go", "Rust", "Swift", "Kotlin", "TypeScript"]
    prompts = [f"Write a one-sentence description of {topic} programming language." for topic in topics[:batch_size]]
    
    # Process in different batch sizes
    batch_sizes = [1, 2, 5, batch_size]
    results = []
    
    for size in batch_sizes:
        print(f"\nProcessing with batch size {size}...")
        
        start_time = time.time()
        batches = [prompts[i:i+size] for i in range(0, len(prompts), size)]
        
        all_results = []
        for batch in batches:
            # Process each batch
            batch_results, _ = await process_prompts_async(batch)
            all_results.extend(batch_results)
        
        total_time = time.time() - start_time
        
        results.append({
            "batch_size": size,
            "total_time": total_time,
            "results": all_results
        })
        
        print(f"Total time: {total_time:.2f} seconds")
    
    # Summary
    print("\nBATCH PROCESSING SUMMARY")
    print("-" * 40)
    
    for result in results:
        size = result["batch_size"]
        time_taken = result["total_time"]
        throughput = batch_size / time_taken
        
        print(f"Batch size {size}: {time_taken:.2f} seconds, {throughput:.2f} requests/second")
    
    # Calculate optimal batch size
    optimal = max(results, key=lambda x: batch_size / x["total_time"])
    print(f"\nOptimal batch size: {optimal['batch_size']} (throughput: {batch_size / optimal['total_time']:.2f} req/sec)")

if __name__ == "__main__":
    print("Module 12: Performance Optimization - Asynchronous Processing")
    print("\nThis module demonstrates how to implement asynchronous processing for chatbots.")
    print("\nNote: You need to install aiohttp to run this module:")
    print("pip install aiohttp")
    
    while True:
        print("\nChoose an option:")
        print("1. Run automated demonstration")
        print("2. Interactive demo")
        print("3. Batch processing demo")
        print("4. Exit")
        
        choice = input("> ").strip()
        
        if choice == "1":
            demonstrate_async()
        elif choice == "2":
            interactive_async_demo()
        elif choice == "3":
            asyncio.run(batch_processing_demo())
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")
