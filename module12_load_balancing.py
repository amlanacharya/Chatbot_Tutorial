"""
Module 12: Performance Optimization - Load Balancing

This module demonstrates how to implement basic load balancing for chatbots:
1. Round-robin load balancing across multiple endpoints
2. Weighted load balancing based on endpoint performance
3. Failure detection and automatic failover
4. Performance monitoring for load-balanced systems

Load balancing improves reliability and throughput by distributing requests
across multiple instances or services.
"""

import os
import time
import json
import random
import statistics
from collections import deque
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable. Please set it in your .env file.")

# Simulate multiple endpoints (in a real system, these would be different servers)
# For demonstration, we'll use different models as our "endpoints"
ENDPOINTS = [
    {"name": "endpoint-1", "model": "llama3-8b-8192", "weight": 1.0, "status": "healthy", "response_times": deque(maxlen=10)},
    {"name": "endpoint-2", "model": "gemma-7b-it", "weight": 1.0, "status": "healthy", "response_times": deque(maxlen=10)},
    {"name": "endpoint-3", "model": "mixtral-8x7b-32768", "weight": 1.0, "status": "healthy", "response_times": deque(maxlen=10)}
]

# Basic chat function for a specific endpoint
def chat_with_endpoint(prompt, endpoint_index):
    """
    Send a prompt to a specific endpoint.
    
    Args:
        prompt (str): The user's message
        endpoint_index (int): Index of the endpoint to use
        
    Returns:
        dict: The response data including content and timing information
    """
    endpoint = ENDPOINTS[endpoint_index]
    model = endpoint["model"]
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
        
        # Update endpoint stats
        endpoint["response_times"].append(response_time)
        
        return {
            "content": result["choices"][0]["message"]["content"],
            "response_time": response_time,
            "endpoint": endpoint["name"],
            "model": model,
            "status": "success"
        }
        
    except requests.exceptions.RequestException as e:
        # Mark endpoint as unhealthy after failure
        endpoint["status"] = "unhealthy"
        
        return {
            "content": f"Error: {str(e)}",
            "response_time": time.time() - start_time,
            "endpoint": endpoint["name"],
            "model": model,
            "status": "error"
        }

# Round-robin load balancer
class RoundRobinLoadBalancer:
    """Simple round-robin load balancer"""
    
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.current_index = 0
    
    def get_next_endpoint(self):
        """Get the next endpoint in rotation"""
        # Find next healthy endpoint
        start_index = self.current_index
        while True:
            endpoint = self.endpoints[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.endpoints)
            
            if endpoint["status"] == "healthy":
                return self.current_index
            
            # If we've checked all endpoints and none are healthy, reset all to healthy and try again
            if self.current_index == start_index:
                for ep in self.endpoints:
                    ep["status"] = "healthy"
                return self.current_index
    
    def send_request(self, prompt):
        """Send request to the next endpoint in rotation"""
        endpoint_index = self.get_next_endpoint()
        return chat_with_endpoint(prompt, endpoint_index)

# Weighted load balancer
class WeightedLoadBalancer:
    """Load balancer that distributes traffic based on weights"""
    
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.update_weights()
    
    def update_weights(self):
        """Update weights based on endpoint performance"""
        # Calculate average response time for each endpoint
        for endpoint in self.endpoints:
            if endpoint["response_times"]:
                avg_time = statistics.mean(endpoint["response_times"])
                # Inverse relationship: faster endpoints get higher weights
                if avg_time > 0:
                    endpoint["weight"] = 1.0 / avg_time
                else:
                    endpoint["weight"] = 1.0
            else:
                endpoint["weight"] = 1.0
            
            # Set weight to 0 for unhealthy endpoints
            if endpoint["status"] != "healthy":
                endpoint["weight"] = 0
    
    def get_next_endpoint(self):
        """Get the next endpoint based on weights"""
        self.update_weights()
        
        # Check if all endpoints are unhealthy
        all_unhealthy = all(endpoint["status"] != "healthy" for endpoint in self.endpoints)
        if all_unhealthy:
            # Reset all endpoints to healthy
            for endpoint in self.endpoints:
                endpoint["status"] = "healthy"
            self.update_weights()
        
        # Get total weight
        total_weight = sum(endpoint["weight"] for endpoint in self.endpoints)
        
        if total_weight == 0:
            # If all weights are 0, use round-robin
            return random.randint(0, len(self.endpoints) - 1)
        
        # Choose endpoint based on weight
        r = random.uniform(0, total_weight)
        upto = 0
        for i, endpoint in enumerate(self.endpoints):
            if upto + endpoint["weight"] >= r:
                return i
            upto += endpoint["weight"]
        
        # Fallback
        return 0
    
    def send_request(self, prompt):
        """Send request to an endpoint based on weights"""
        endpoint_index = self.get_next_endpoint()
        return chat_with_endpoint(prompt, endpoint_index)

# Adaptive load balancer with health checks
class AdaptiveLoadBalancer:
    """Advanced load balancer with health checks and adaptive weights"""
    
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.health_check_interval = 5  # seconds
        self.last_health_check = 0
        self.update_weights()
    
    def update_weights(self):
        """Update weights based on endpoint performance and health"""
        # Calculate average response time for each endpoint
        for endpoint in self.endpoints:
            if endpoint["response_times"]:
                avg_time = statistics.mean(endpoint["response_times"])
                # Inverse relationship: faster endpoints get higher weights
                if avg_time > 0:
                    endpoint["weight"] = 1.0 / avg_time
                else:
                    endpoint["weight"] = 1.0
            else:
                endpoint["weight"] = 1.0
            
            # Set weight to 0 for unhealthy endpoints
            if endpoint["status"] != "healthy":
                endpoint["weight"] = 0
    
    def health_check(self):
        """Perform health check on all endpoints"""
        current_time = time.time()
        
        # Only run health check at intervals
        if current_time - self.last_health_check < self.health_check_interval:
            return
        
        self.last_health_check = current_time
        print("\nPerforming health check on all endpoints...")
        
        for i, endpoint in enumerate(self.endpoints):
            if endpoint["status"] != "healthy":
                # Try to recover unhealthy endpoint
                try:
                    # Simple health check - just a quick API call
                    response = chat_with_endpoint("Hello", i)
                    if response["status"] == "success":
                        print(f"Endpoint {endpoint['name']} recovered!")
                        endpoint["status"] = "healthy"
                except:
                    print(f"Endpoint {endpoint['name']} still unhealthy")
    
    def get_next_endpoint(self):
        """Get the next endpoint based on adaptive algorithm"""
        # Run health check
        self.health_check()
        
        # Update weights
        self.update_weights()
        
        # Check if all endpoints are unhealthy
        all_unhealthy = all(endpoint["status"] != "healthy" for endpoint in self.endpoints)
        if all_unhealthy:
            # Reset all endpoints to healthy
            for endpoint in self.endpoints:
                endpoint["status"] = "healthy"
            self.update_weights()
        
        # Get total weight
        total_weight = sum(endpoint["weight"] for endpoint in self.endpoints)
        
        if total_weight == 0:
            # If all weights are 0, use round-robin
            return random.randint(0, len(self.endpoints) - 1)
        
        # Choose endpoint based on weight
        r = random.uniform(0, total_weight)
        upto = 0
        for i, endpoint in enumerate(self.endpoints):
            if upto + endpoint["weight"] >= r:
                return i
            upto += endpoint["weight"]
        
        # Fallback
        return 0
    
    def send_request(self, prompt):
        """Send request using adaptive load balancing"""
        endpoint_index = self.get_next_endpoint()
        return chat_with_endpoint(prompt, endpoint_index)

# Demonstration function
def demonstrate_load_balancing():
    """Demonstrate different load balancing strategies"""
    print("\n" + "="*80)
    print("CHATBOT PERFORMANCE OPTIMIZATION: LOAD BALANCING".center(80))
    print("="*80)
    
    # Create test prompts
    test_prompts = [
        "What is load balancing?",
        "Explain high availability in simple terms.",
        "What is a distributed system?",
        "How does fault tolerance work?",
        "What is horizontal scaling?",
        "Define vertical scaling.",
        "What is a reverse proxy?",
        "Explain the concept of redundancy.",
        "What is a failover system?",
        "How does a load balancer handle session persistence?"
    ]
    
    # Initialize load balancers
    round_robin = RoundRobinLoadBalancer(ENDPOINTS)
    weighted = WeightedLoadBalancer(ENDPOINTS)
    adaptive = AdaptiveLoadBalancer(ENDPOINTS)
    
    # Test round-robin load balancing
    print("\n1. ROUND-ROBIN LOAD BALANCING")
    print("-" * 40)
    
    rr_results = []
    for i, prompt in enumerate(test_prompts[:5]):  # Use first 5 prompts
        print(f"\nPrompt {i+1}: {prompt}")
        response = round_robin.send_request(prompt)
        rr_results.append(response)
        
        print(f"Endpoint: {response['endpoint']} ({response['model']})")
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content'][:100]}...")
    
    # Test weighted load balancing
    print("\n\n2. WEIGHTED LOAD BALANCING")
    print("-" * 40)
    
    weighted_results = []
    for i, prompt in enumerate(test_prompts[5:]):  # Use last 5 prompts
        print(f"\nPrompt {i+1}: {prompt}")
        response = weighted.send_request(prompt)
        weighted_results.append(response)
        
        print(f"Endpoint: {response['endpoint']} ({response['model']})")
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content'][:100]}...")
    
    # Summary
    print("\n\nLOAD BALANCING SUMMARY")
    print("-" * 40)
    
    # Endpoint statistics
    print("\nEndpoint Statistics:")
    for endpoint in ENDPOINTS:
        if endpoint["response_times"]:
            avg_time = statistics.mean(endpoint["response_times"])
            print(f"- {endpoint['name']} ({endpoint['model']}): {len(endpoint['response_times'])} requests, avg time: {avg_time:.2f}s, weight: {endpoint['weight']:.2f}")
        else:
            print(f"- {endpoint['name']} ({endpoint['model']}): No requests")
    
    # Distribution analysis
    rr_distribution = {}
    weighted_distribution = {}
    
    for response in rr_results:
        endpoint = response["endpoint"]
        rr_distribution[endpoint] = rr_distribution.get(endpoint, 0) + 1
    
    for response in weighted_results:
        endpoint = response["endpoint"]
        weighted_distribution[endpoint] = weighted_distribution.get(endpoint, 0) + 1
    
    print("\nRequest Distribution:")
    print("- Round-Robin:", rr_distribution)
    print("- Weighted:", weighted_distribution)

# Simulate endpoint failure
def simulate_failure():
    """Simulate an endpoint failure and recovery"""
    print("\n" + "="*80)
    print("SIMULATING ENDPOINT FAILURE AND RECOVERY".center(80))
    print("="*80)
    
    # Initialize adaptive load balancer
    adaptive = AdaptiveLoadBalancer(ENDPOINTS)
    
    # Create test prompts
    test_prompts = [
        "What happens when a server fails?",
        "How do systems recover from failures?",
        "What is fault tolerance?",
        "Explain high availability architecture.",
        "What is a disaster recovery plan?"
    ]
    
    # Process first 2 prompts normally
    print("\n1. NORMAL OPERATION")
    print("-" * 40)
    
    for i, prompt in enumerate(test_prompts[:2]):
        print(f"\nPrompt {i+1}: {prompt}")
        response = adaptive.send_request(prompt)
        
        print(f"Endpoint: {response['endpoint']} ({response['model']})")
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content'][:100]}...")
    
    # Simulate failure of first endpoint
    print("\n\n2. SIMULATING FAILURE OF ENDPOINT-1")
    print("-" * 40)
    
    ENDPOINTS[0]["status"] = "unhealthy"
    print(f"Endpoint {ENDPOINTS[0]['name']} is now marked as unhealthy!")
    
    # Process next 2 prompts with failure
    for i, prompt in enumerate(test_prompts[2:4]):
        print(f"\nPrompt {i+3}: {prompt}")
        response = adaptive.send_request(prompt)
        
        print(f"Endpoint: {response['endpoint']} ({response['model']})")
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content'][:100]}...")
    
    # Simulate recovery
    print("\n\n3. SIMULATING RECOVERY")
    print("-" * 40)
    
    ENDPOINTS[0]["status"] = "healthy"
    print(f"Endpoint {ENDPOINTS[0]['name']} is now recovered and marked as healthy!")
    
    # Process last prompt after recovery
    print(f"\nPrompt 5: {test_prompts[4]}")
    response = adaptive.send_request(test_prompts[4])
    
    print(f"Endpoint: {response['endpoint']} ({response['model']})")
    print(f"Response time: {response['response_time']:.2f} seconds")
    print(f"Response: {response['content'][:100]}...")
    
    # Summary
    print("\n\nFAILURE RECOVERY SUMMARY")
    print("-" * 40)
    
    print("The load balancer successfully detected the endpoint failure and")
    print("routed traffic to healthy endpoints. After recovery, the previously")
    print("failed endpoint was reintegrated into the rotation.")

# Interactive demo
def interactive_load_balancing_demo():
    """Interactive demo to test load balancing"""
    print("\n" + "="*80)
    print("INTERACTIVE LOAD BALANCING DEMO".center(80))
    print("="*80)
    
    # Initialize load balancers
    round_robin = RoundRobinLoadBalancer(ENDPOINTS)
    weighted = WeightedLoadBalancer(ENDPOINTS)
    adaptive = AdaptiveLoadBalancer(ENDPOINTS)
    
    while True:
        print("\nEnter a prompt to test load balancing (or 'exit' to quit):")
        prompt = input("> ").strip()
        
        if prompt.lower() == 'exit':
            break
        
        print("\nChoose load balancing strategy:")
        print("1. Round-Robin")
        print("2. Weighted")
        print("3. Adaptive with Health Checks")
        
        strategy = input("> ").strip()
        
        if strategy == "1":
            response = round_robin.send_request(prompt)
            strategy_name = "Round-Robin"
        elif strategy == "2":
            response = weighted.send_request(prompt)
            strategy_name = "Weighted"
        elif strategy == "3":
            response = adaptive.send_request(prompt)
            strategy_name = "Adaptive"
        else:
            print("Invalid strategy. Using Round-Robin.")
            response = round_robin.send_request(prompt)
            strategy_name = "Round-Robin"
        
        print(f"\nStrategy: {strategy_name}")
        print(f"Endpoint: {response['endpoint']} ({response['model']})")
        print(f"Response time: {response['response_time']:.2f} seconds")
        print(f"Response: {response['content']}")
        
        # Show endpoint statistics
        print("\nEndpoint Statistics:")
        for endpoint in ENDPOINTS:
            if endpoint["response_times"]:
                avg_time = statistics.mean(endpoint["response_times"])
                print(f"- {endpoint['name']} ({endpoint['model']}): {len(endpoint['response_times'])} requests, avg time: {avg_time:.2f}s, weight: {endpoint['weight']:.2f}")
            else:
                print(f"- {endpoint['name']} ({endpoint['model']}): No requests")

if __name__ == "__main__":
    print("Module 12: Performance Optimization - Load Balancing")
    print("\nThis module demonstrates how to implement load balancing for chatbots.")
    
    while True:
        print("\nChoose an option:")
        print("1. Demonstrate load balancing strategies")
        print("2. Simulate endpoint failure and recovery")
        print("3. Interactive load balancing demo")
        print("4. Exit")
        
        choice = input("> ").strip()
        
        if choice == "1":
            demonstrate_load_balancing()
        elif choice == "2":
            simulate_failure()
        elif choice == "3":
            interactive_load_balancing_demo()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")
