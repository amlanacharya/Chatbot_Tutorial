"""
Module 13: Deployment Options

This module demonstrates different deployment options for AI chatbots:
1. Local deployment with Docker
2. Cloud deployment considerations
3. Scaling strategies
4. Monitoring and logging setup

These deployment options help you move from development to production environments.
"""

import os
import json
import logging
import time
from datetime import datetime
import argparse
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, start_http_server
from pythonjsonlogger import jsonlogger

# Load environment variables
load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Warning: Missing GROQ_API_KEY environment variable. Some features may not work.")

# Set up logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s',
    rename_fields={'levelname': 'level', 'asctime': 'timestamp'}
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Set up metrics
REQUEST_COUNT = Counter('chatbot_requests_total', 'Total number of requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('chatbot_request_latency_seconds', 'Request latency in seconds', ['endpoint'])

# Initialize Flask app
app = Flask(__name__)

def chat_with_groq(prompt, model="llama3-8b-8192"):
    """Send a chat request to the Groq API"""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not set"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data)
        response_time = time.time() - start_time
        
        # Log request details
        logger.info({
            "event": "api_request",
            "model": model,
            "status_code": response.status_code,
            "response_time": response_time,
            "prompt_length": len(prompt)
        })
        
        # Update metrics
        REQUEST_LATENCY.labels(endpoint='chat').observe(response_time)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        REQUEST_COUNT.labels(endpoint='chat', status='success').inc()
        
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        logger.error({
            "event": "api_error",
            "error": str(e),
            "model": model
        })
        REQUEST_COUNT.labels(endpoint='chat', status='error').inc()
        return f"Error: {str(e)}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Chat API endpoint"""
    data = request.json
    
    if not data or 'prompt' not in data:
        REQUEST_COUNT.labels(endpoint='chat', status='error').inc()
        return jsonify({"error": "Missing prompt parameter"}), 400
    
    prompt = data['prompt']
    model = data.get('model', "llama3-8b-8192")
    
    # Log request
    logger.info({
        "event": "chat_request",
        "model": model,
        "prompt_length": len(prompt),
        "client_ip": request.remote_addr
    })
    
    # Process request with timing
    with REQUEST_LATENCY.labels(endpoint='chat').time():
        response = chat_with_groq(prompt, model)
    
    return jsonify({
        "response": response,
        "model": model,
        "timestamp": datetime.now().isoformat()
    })

def start_metrics_server(port=8000):
    """Start Prometheus metrics server"""
    start_http_server(port)
    logger.info(f"Metrics server started on port {port}")

def display_deployment_info():
    """Display information about deployment options"""
    print("\n" + "="*80)
    print("Module 13: Deployment Options".center(80))
    print("="*80)
    
    print("\nThis module demonstrates different deployment options for AI chatbots:")
    print("1. Local deployment with Docker")
    print("2. Cloud deployment considerations")
    print("3. Scaling strategies")
    print("4. Monitoring and logging setup")
    
    print("\n" + "-"*80)
    print("Containerization with Docker".center(80))
    print("-"*80)
    
    print("\nDocker provides a consistent environment for your application:")
    print("- Dockerfile: Defines the container image")
    print("- docker-compose.yml: Orchestrates multiple containers")
    print("- Environment variables: Managed through .env files or Docker secrets")
    
    print("\nTo build and run the Docker container:")
    print("```bash")
    print("docker build -t chatbot-app .")
    print("docker run -p 5000:5000 -p 8000:8000 chatbot-app")
    print("```")
    
    print("\n" + "-"*80)
    print("Cloud Deployment Options".center(80))
    print("-"*80)
    
    print("\nYour chatbot can be deployed to various cloud platforms:")
    print("\n1. AWS:")
    print("   - AWS Lambda: Serverless, pay-per-use")
    print("   - ECS/EKS: Container orchestration")
    print("   - Elastic Beanstalk: PaaS solution")
    
    print("\n2. Azure:")
    print("   - Azure Functions: Serverless option")
    print("   - Azure Container Instances: Simple container deployment")
    print("   - Azure Kubernetes Service: Full orchestration")
    
    print("\n3. Google Cloud Platform:")
    print("   - Cloud Run: Serverless containers")
    print("   - Cloud Functions: Event-driven serverless")
    print("   - GKE: Managed Kubernetes")
    
    print("\n" + "-"*80)
    print("Scaling Considerations".center(80))
    print("-"*80)
    
    print("\nAs your chatbot grows, consider these scaling strategies:")
    print("- Horizontal scaling: Add more instances")
    print("- Vertical scaling: Increase resources per instance")
    print("- Load balancing: Distribute traffic across instances")
    print("- Caching: Reduce redundant API calls")
    print("- Database scaling: Handle increased data volume")
    
    print("\n" + "-"*80)
    print("Monitoring and Logging".center(80))
    print("-"*80)
    
    print("\nProper monitoring helps identify issues before they affect users:")
    print("- Health checks: Verify service availability")
    print("- Metrics: Track performance and usage")
    print("- Logging: Record events for debugging")
    print("- Alerting: Get notified of problems")
    
    print("\nThis module includes:")
    print("- Prometheus metrics endpoint (/metrics)")
    print("- JSON structured logging")
    print("- Health check endpoint (/health)")
    
    print("\n" + "="*80)

def run_local_server(host='0.0.0.0', port=5000, metrics_port=8000):
    """Run the Flask server locally"""
    # Start metrics server in a separate thread
    import threading
    metrics_thread = threading.Thread(target=start_metrics_server, args=(metrics_port,), daemon=True)
    metrics_thread.start()
    
    # Run Flask app
    print(f"\nStarting Flask server on http://{host}:{port}")
    print(f"Metrics available at http://{host}:{metrics_port}/metrics")
    print(f"Health check available at http://{host}:{port}/health")
    print("\nPress CTRL+C to stop the server")
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Module 13: Deployment Options')
    parser.add_argument('--run', action='store_true', help='Run the local server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--metrics-port', type=int, default=8000, help='Port for Prometheus metrics')
    
    args = parser.parse_args()
    
    # Display deployment information
    display_deployment_info()
    
    if args.run:
        run_local_server(args.host, args.port, args.metrics_port)
    else:
        print("\nTo run the server, use the --run flag:")
        print("python module13.py --run")
        print("\nFor more options:")
        print("python module13.py --help")
