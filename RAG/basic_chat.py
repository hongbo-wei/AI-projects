# Program 1: Direct interaction with DeepSeek 7B
import ollama

# Initialize Ollama client
client = ollama.Client()

# Chat completion example
response = client.chat(
    model="deepseek-r1:7b",  # Model name from Ollama
    messages=[{"role": "user", "content": "Explain quantum computing in simple terms"}]
)
print("🤖 Response:", response["message"]["content"])