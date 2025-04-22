"""
Module 12: Performance Optimization - Caching Strategies

This module demonstrates different caching strategies to improve chatbot performance:
1. Simple in-memory caching
2. LRU (Least Recently Used) cache
3. TTL (Time To Live) cache

These caching mechanisms can significantly reduce API calls and improve response times.
"""

import os
import time
import json
import hashlib
import requests
from collections import OrderedDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Base chat function without caching (for comparison)
def chat_without_cache(prompt, model="llama3-8b-8192"):
    """
    Send a prompt to the Groq API without any caching.
    
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
            "cache_hit": False
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "content": f"Error: {str(e)}",
            "response_time": time.time() - start_time,
            "cache_hit": False
        }

# 1. Simple In-Memory Cache
class SimpleCache:
    """A simple dictionary-based cache"""
    
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get_key(self, prompt, model):
        """Generate a cache key from prompt and model"""
        return hashlib.md5(f"{prompt}:{model}".encode()).hexdigest()
    
    def get(self, prompt, model):
        """Get a response from cache if it exists"""
        key = self.get_key(prompt, model)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, prompt, model, response):
        """Store a response in the cache"""
        key = self.get_key(prompt, model)
        self.cache[key] = response
    
    def clear(self):
        """Clear the cache"""
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }

# 2. LRU Cache (Least Recently Used)
class LRUCache:
    """A cache that removes least recently used items when it reaches capacity"""
    
    def __init__(self, capacity=100):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
    
    def get_key(self, prompt, model):
        """Generate a cache key from prompt and model"""
        return hashlib.md5(f"{prompt}:{model}".encode()).hexdigest()
    
    def get(self, prompt, model):
        """Get a response from cache if it exists, and move it to the end (most recently used)"""
        key = self.get_key(prompt, model)
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, prompt, model, response):
        """Store a response in the cache, removing least recently used item if at capacity"""
        key = self.get_key(prompt, model)
        
        # If key exists, update it and move to end
        if key in self.cache:
            self.cache.move_to_end(key)
        
        # Add new item
        self.cache[key] = response
        
        # Remove oldest item if over capacity
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def clear(self):
        """Clear the cache"""
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total > 0 else 0
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }

# 3. TTL Cache (Time To Live)
class TTLCache:
    """A cache where entries expire after a specified time"""
    
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.expiry = {}
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def get_key(self, prompt, model):
        """Generate a cache key from prompt and model"""
        return hashlib.md5(f"{prompt}:{model}".encode()).hexdigest()
    
    def get(self, prompt, model):
        """Get a response from cache if it exists and hasn't expired"""
        key = self.get_key(prompt, model)
        current_time = time.time()
        
        if key in self.cache and current_time < self.expiry[key]:
            self.hits += 1
            return self.cache[key]
        
        # Remove if expired
        if key in self.cache and current_time >= self.expiry[key]:
            del self.cache[key]
            del self.expiry[key]
        
        self.misses += 1
        return None
    
    def set(self, prompt, model, response):
        """Store a response in the cache with an expiration time"""
        key = self.get_key(prompt, model)
        self.cache[key] = response
        self.expiry[key] = time.time() + self.ttl_seconds
    
    def clear(self):
        """Clear the cache"""
        self.cache = {}
        self.expiry = {}
        self.hits = 0
        self.misses = 0
    
    def cleanup(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [k for k, exp in self.expiry.items() if current_time >= exp]
        
        for key in expired_keys:
            del self.cache[key]
            del self.expiry[key]
        
        return len(expired_keys)
    
    def stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total > 0 else 0
        return {
            "size": len(self.cache),
            "ttl": self.ttl_seconds,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }

# Chat functions with different caching strategies
def chat_with_simple_cache(prompt, model="llama3-8b-8192", cache=None):
    """Chat function with simple in-memory caching"""
    if cache is None:
        cache = SimpleCache()
    
    # Check cache first
    cached_response = cache.get(prompt, model)
    if cached_response:
        cached_response["cache_hit"] = True
        return cached_response
    
    # If not in cache, call API
    response = chat_without_cache(prompt, model)
    
    # Store in cache
    cache.set(prompt, model, response)
    
    return response

def chat_with_lru_cache(prompt, model="llama3-8b-8192", cache=None, capacity=100):
    """Chat function with LRU caching"""
    if cache is None:
        cache = LRUCache(capacity=capacity)
    
    # Check cache first
    cached_response = cache.get(prompt, model)
    if cached_response:
        cached_response["cache_hit"] = True
        return cached_response
    
    # If not in cache, call API
    response = chat_without_cache(prompt, model)
    
    # Store in cache
    cache.set(prompt, model, response)
    
    return response

def chat_with_ttl_cache(prompt, model="llama3-8b-8192", cache=None, ttl_seconds=3600):
    """Chat function with TTL caching"""
    if cache is None:
        cache = TTLCache(ttl_seconds=ttl_seconds)
    
    # Check cache first
    cached_response = cache.get(prompt, model)
    if cached_response:
        cached_response["cache_hit"] = True
        return cached_response
    
    # If not in cache, call API
    response = chat_without_cache(prompt, model)
    
    # Store in cache
    cache.set(prompt, model, response)
    
    # Cleanup expired entries
    cache.cleanup()
    
    return response

# Demonstration function
def demonstrate_caching():
    """Demonstrate the different caching strategies"""
    print("\n" + "="*80)
    print("CHATBOT PERFORMANCE OPTIMIZATION: CACHING STRATEGIES".center(80))
    print("="*80)
    
    # Create test prompts
    test_prompts = [
        "What is machine learning?",
        "Explain the concept of neural networks.",
        "What is the difference between AI and ML?",
        "What is machine learning?",  # Repeated to demonstrate cache hit
        "Explain the concept of neural networks."  # Repeated to demonstrate cache hit
    ]
    
    # Initialize caches
    simple_cache = SimpleCache()
    lru_cache = LRUCache(capacity=10)
    ttl_cache = TTLCache(ttl_seconds=3600)
    
    # Test without cache
    print("\n1. WITHOUT CACHING")
    print("-" * 40)
    no_cache_times = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        response = chat_without_cache(prompt)
        no_cache_times.append(response["response_time"])
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
    
    avg_time_no_cache = sum(no_cache_times) / len(no_cache_times)
    print(f"\nAverage response time without cache: {avg_time_no_cache:.2f} seconds")
    
    # Test with simple cache
    print("\n\n2. WITH SIMPLE CACHE")
    print("-" * 40)
    simple_cache_times = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        response = chat_with_simple_cache(prompt, cache=simple_cache)
        simple_cache_times.append(response["response_time"])
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
    
    avg_time_simple = sum(simple_cache_times) / len(simple_cache_times)
    print(f"\nAverage response time with simple cache: {avg_time_simple:.2f} seconds")
    print(f"Cache stats: {json.dumps(simple_cache.stats(), indent=2)}")
    
    # Test with LRU cache
    print("\n\n3. WITH LRU CACHE")
    print("-" * 40)
    lru_cache_times = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        response = chat_with_lru_cache(prompt, cache=lru_cache)
        lru_cache_times.append(response["response_time"])
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
    
    avg_time_lru = sum(lru_cache_times) / len(lru_cache_times)
    print(f"\nAverage response time with LRU cache: {avg_time_lru:.2f} seconds")
    print(f"Cache stats: {json.dumps(lru_cache.stats(), indent=2)}")
    
    # Test with TTL cache
    print("\n\n4. WITH TTL CACHE")
    print("-" * 40)
    ttl_cache_times = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        response = chat_with_ttl_cache(prompt, cache=ttl_cache)
        ttl_cache_times.append(response["response_time"])
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
    
    avg_time_ttl = sum(ttl_cache_times) / len(ttl_cache_times)
    print(f"\nAverage response time with TTL cache: {avg_time_ttl:.2f} seconds")
    print(f"Cache stats: {json.dumps(ttl_cache.stats(), indent=2)}")
    
    # Summary
    print("\n\nPERFORMANCE SUMMARY")
    print("-" * 40)
    print(f"Average response time without cache: {avg_time_no_cache:.2f} seconds")
    print(f"Average response time with simple cache: {avg_time_simple:.2f} seconds")
    print(f"Average response time with LRU cache: {avg_time_lru:.2f} seconds")
    print(f"Average response time with TTL cache: {avg_time_ttl:.2f} seconds")
    
    # Calculate improvement
    improvement_simple = ((avg_time_no_cache - avg_time_simple) / avg_time_no_cache) * 100
    improvement_lru = ((avg_time_no_cache - avg_time_lru) / avg_time_no_cache) * 100
    improvement_ttl = ((avg_time_no_cache - avg_time_ttl) / avg_time_no_cache) * 100
    
    print(f"\nImprovement with simple cache: {improvement_simple:.2f}%")
    print(f"Improvement with LRU cache: {improvement_lru:.2f}%")
    print(f"Improvement with TTL cache: {improvement_ttl:.2f}%")

# Interactive demo
def interactive_demo():
    """Interactive demo to test different caching strategies"""
    print("\n" + "="*80)
    print("INTERACTIVE CACHING DEMO".center(80))
    print("="*80)
    
    # Initialize caches
    simple_cache = SimpleCache()
    lru_cache = LRUCache(capacity=10)
    ttl_cache = TTLCache(ttl_seconds=3600)
    
    while True:
        print("\nEnter a prompt to test caching strategies (or 'exit' to quit):")
        prompt = input("> ").strip()
        
        if prompt.lower() == 'exit':
            break
        
        # Test all caching strategies
        print("\nTesting different caching strategies...")
        
        # No cache
        print("\n1. WITHOUT CACHING")
        start = time.time()
        response = chat_without_cache(prompt)
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content'][:100]}...")
        
        # Simple cache
        print("\n2. WITH SIMPLE CACHE")
        response = chat_with_simple_cache(prompt, cache=simple_cache)
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
        print(f"Cache stats: {json.dumps(simple_cache.stats(), indent=2)}")
        
        # LRU cache
        print("\n3. WITH LRU CACHE")
        response = chat_with_lru_cache(prompt, cache=lru_cache)
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
        print(f"Cache stats: {json.dumps(lru_cache.stats(), indent=2)}")
        
        # TTL cache
        print("\n4. WITH TTL CACHE")
        response = chat_with_ttl_cache(prompt, cache=ttl_cache)
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Cache hit: {response['cache_hit']}")
        print(f"Cache stats: {json.dumps(ttl_cache.stats(), indent=2)}")

if __name__ == "__main__":
    print("Module 12: Performance Optimization - Caching Strategies")
    print("\nThis module demonstrates different caching strategies to improve chatbot performance.")
    
    while True:
        print("\nChoose an option:")
        print("1. Run automated demonstration")
        print("2. Interactive demo")
        print("3. Exit")
        
        choice = input("> ").strip()
        
        if choice == "1":
            demonstrate_caching()
        elif choice == "2":
            interactive_demo()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
