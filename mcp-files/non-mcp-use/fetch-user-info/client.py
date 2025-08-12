# mcp_client.py
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama2"

def call_ollama(prompt):
    res = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False})
    return res.json().get("response")

def determine_action(user_input):
    prompt = f"""
You are an intelligent assistant. Given a user's question, decide which microservice is needed.

Available MCP Servers:
- user_info: handles user data from https://fake-json-api.mock.beeceptor.com/users

Return your answer in this JSON format:
{{
  "action": "...",
  "target_server": "..."
}}

User: {user_input}
"""
    response = call_ollama(prompt)
    try:
        return json.loads(response)
    except:
        print("Failed to parse LLM response:", response)
        return None

def fetch_from_mcp_server(server):
    if server == "user_info":
        res = requests.get("http://localhost:8000/users")
        return res.json()
    return {"error": "Unknown server"}

def generate_final_response(question, data):
    prompt = f"""
You are a chatbot. The user asked: "{question}"
Here is the data retrieved from the API: {data}
Use the data to answer the user in a friendly, helpful way.
"""
    return call_ollama(prompt)

def main():
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Step 1: Get LLM decision
        decision = determine_action(user_input)
        if not decision:
            print("Couldn't understand the command.")
            continue

        # Step 2: Call appropriate MCP server
        data = fetch_from_mcp_server(decision['target_server'])

        # Step 3: Ask LLM to generate final response
        final_response = generate_final_response(user_input, data)
        print("Bot:", final_response)

if __name__ == "__main__":
    main()
