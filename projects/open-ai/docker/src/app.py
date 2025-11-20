import os
from flask import Flask, request, jsonify
from openai import OpenAI

# OpenAI / OpenAI-compatible endpoints
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL") # For custom endpoints

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
print(f"OpenAI client initialized. Base URL: {openai_base_url or 'default'}")

app = Flask(__name__)

@app.route('/computation', methods=['POST'])
def computation():
    """
    Accepts a POST request with a JSON body containing 'model' and 'prompt' keys,
    queries the OpenAI API, and returns the response.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    prompt = data.get('prompt')
    # The 'provider' part (e.g., 'openai/') is now optional and will be ignored.
    model_name = (data.get('model') or 'openai/gpt-4o').split('/')[-1]
    

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    print(f"--> Received request for model: {model_name}")
    print(f"--> Prompt (first 80 chars): {prompt[:80]}...")

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
        )
        output = chat_completion.choices[0].message.content
        return jsonify({"output": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8083))
    app.run(host='0.0.0.0', port=port)