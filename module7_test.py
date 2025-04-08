import requests
import json
import time
import pandas as pd

API_URL = "http://localhost:5000"
MODELS = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
TEST_PROMPTS = [
    "Explain the difference between machine learning and deep learning",
    "Write a short poem about artificial intelligence",
    "Summarize the main ideas of reinforcement learning",
    "What are the ethical concerns with large language models?"
]

results = []

for prompt in TEST_PROMPTS:
    for model in MODELS:
        print(f"Testing {model} on: {prompt[:30]}...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                "message": prompt,
                "model": model,
                "session_id": f"test-{model}-{hash(prompt)}"
            }
        )
        
        elapsed_time = time.time() - start_time
        data = response.json()
        
        results.append({
            "model": model,
            "prompt": prompt,
            "response": data.get("response", "Error"),
            "time": elapsed_time,
            "tokens": data.get("token_count", 0)
        })

# Save results
df = pd.DataFrame(results)
df.to_csv("model_comparison_results.csv", index=False)
print("Evaluation complete!")