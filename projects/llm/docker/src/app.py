import os
from flask import Flask, request, jsonify
from openai import OpenAI

# --- Client Initialization ---

clients = {}

# LLMRouter (OpenAI compatible)
llmrouter_api_key = os.getenv("LLMROUTER_API_KEY")
llmrouter_base_url = os.getenv("LLMROUTER_BASE_URL")
if llmrouter_api_key and llmrouter_base_url:
    clients["llmrouter"] = OpenAI(api_key=llmrouter_api_key, base_url=llmrouter_base_url)
    print(f"LLMRouter client initialized for: {llmrouter_base_url}")

# Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    import google.generativeai as genai
    genai.configure(api_key=gemini_api_key)
    clients["gemini"] = genai
    print("Gemini client initialized.")

if not clients:
    raise ValueError("No LLM provider credentials found. Please set GEMINI_API_KEY or LLMROUTER variables.")

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

    try:
        if provider == "gemini":
            if "gemini" not in clients:
                return jsonify({"error": "Gemini client not configured."}), 500
            genai_client = clients[provider]
            model = genai_client.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            output = response.text
            return jsonify({"output": output})
        else: # All other providers go through the LLM Router
            if "llmrouter" not in clients:
                return jsonify({"error": "LLMRouter client not configured."}), 500
            router_client = clients["llmrouter"]
            chat_completion = router_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_identifier, # Pass the full identifier to the router
            )
            output = chat_completion.choices[0].message.content
            return jsonify({"output": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8082))
    app.run(host='0.0.0.0', port=port)