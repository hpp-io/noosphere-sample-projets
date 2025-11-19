import os
from flask import Flask, request, jsonify

# --- Client Initialization ---
# Initialize clients based on available environment variables.
# This makes the service flexible, supporting only the providers for which
# credentials are provided.

clients = {}

# OpenAI / OpenAI-compatible endpoints
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL") # For custom endpoints
if openai_api_key:
    from openai import OpenAI
    clients["openai"] = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
    print(f"OpenAI client initialized. Base URL: {openai_base_url or 'default'}")

# Anthropic
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_api_key:
    from anthropic import Anthropic
    clients["anthropic"] = Anthropic(api_key=anthropic_api_key)
    print("Anthropic client initialized.")

# Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    import google.generativeai as genai
    genai.configure(api_key=gemini_api_key)
    clients["gemini"] = genai
    print("Gemini client initialized.")

# Ollama (using OpenAI's client library)
ollama_host = os.getenv("OLLAMA_HOST")  # e.g., http://host.docker.internal:11434
if ollama_host:
    from openai import OpenAI
    clients["ollama"] = OpenAI(
        base_url=f"{ollama_host}/v1",
        api_key='ollama',  # required but ignored by Ollama
    )
    print(f"Ollama client initialized for host: {ollama_host}")

if not clients:
    raise ValueError("No LLM provider credentials found. Please set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, OLLAMA_HOST.")

app = Flask(__name__)

@app.route('/computation', methods=['POST'])
def computation():
    """
    Accepts a POST request with a JSON body containing 'model' and 'prompt' keys.
    Queries the specified model provider and returns the response.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    prompt = data.get('prompt')
    model_identifier = data.get('model')

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400
    if not model_identifier:
        return jsonify({"error": "Missing 'model' in request body"}), 400

    try:
        provider, model_name = model_identifier.split('/', 1)
    except ValueError:
        return jsonify({"error": "Invalid model format. Expected 'provider/model-name'."}), 400

    if provider not in clients:
        return jsonify({"error": f"Provider '{provider}' is not supported or configured."}), 400

    try:
        if provider == "openai" or provider == "ollama":
            client = clients[provider]
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
            )
            output = chat_completion.choices[0].message.content
            return jsonify({"output": output})

        elif provider == "anthropic":
            client = clients[provider]
            message = client.messages.create(
                model=model_name,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            output = message.content[0].text
            return jsonify({"output": output})
        
        elif provider == "gemini":
            genai_client = clients[provider]
            model = genai_client.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            output = response.text
            return jsonify({"output": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8082))
    app.run(host='0.0.0.0', port=port)