import os
import re
import logging
from flask import Flask, request, jsonify, Response
from openai import OpenAI


def detect_mimetype(content):
    """Detect mimetype based on content. Returns 'image/svg+xml' for SVG, 'text/plain' otherwise."""
    if content and re.search(r'<svg\s', content, re.IGNORECASE):
        return 'image/svg+xml'
    return 'text/plain'


def build_message_content(prompt, images=None, provider=None):
    """Build message content for chat completion. Supports multimodal (text + images) input."""
    if not images:
        return prompt

    # Multimodal format: array of content parts
    content = [{"type": "text", "text": prompt}]
    for image_url in images:
        if provider == "anthropic":
            # Claude format
            content.append({"type": "image", "source": {"type": "url", "url": image_url}})
        else:
            # OpenAI format (default)
            content.append({"type": "image_url", "image_url": {"url": image_url}})
    return content

# --- Client Initialization ---

clients = {}

# LLMRouter (OpenAI compatible)
llmrouter_api_key = os.getenv("LLMROUTER_API_KEY")
llmrouter_base_url = os.getenv("LLMROUTER_BASE_URL")
if llmrouter_api_key and llmrouter_base_url:
    clients["llmrouter"] = OpenAI(api_key=llmrouter_api_key, base_url=llmrouter_base_url)
    print(f"LLMRouter client initialized for: {llmrouter_base_url}")
    # Image generation uses a different base URL (without /llm prefix)
    image_base_url = llmrouter_base_url.replace("/llm/v1", "/v1")
    clients["llmrouter_images"] = OpenAI(api_key=llmrouter_api_key, base_url=image_base_url)
    print(f"LLMRouter image client initialized for: {image_base_url}")

# Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    import google.generativeai as genai
    genai.configure(api_key=gemini_api_key)
    clients["gemini"] = genai
    print("Gemini client initialized.")

if not clients:
    raise ValueError("No LLM provider credentials found. Please set GEMINI_API_KEY or LLMROUTER variables.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/computation', methods=['POST'])
def computation():
    """
    Accepts a POST request with a JSON body containing 'model', 'prompt', and optional 'images' or 'image' keys.
    Supports multimodal input (text + images) for vision-capable models.
    Also supports image generation with gpt-image-1 models.

    Image formats supported:
    - images: list of image URLs (e.g., ["https://...", "ipfs://..."])
    - image: object with type and base64 data (e.g., {"type": "image/png", "data": "base64..."})
    """
    data = request.get_json()
    # Log request without full image data to avoid huge logs
    log_data = {k: v for k, v in data.items() if k != 'image'}
    if 'image' in data:
        log_data['image'] = f"<{data['image'].get('type', 'unknown')}, {len(data['image'].get('data', ''))} bytes>"
    logging.info(f"Received request: {log_data}")

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    prompt = data.get('prompt')
    model_identifier = data.get('model')
    images = data.get('images')  # Optional: list of image URLs
    image = data.get('image')    # Optional: single image with base64 data

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400
    if not model_identifier:
        return jsonify({"error": "Missing 'model' in request body"}), 400

    # Check if this is an image generation request
    if model_identifier in ['gpt-image-1', 'gpt-image-1-mini']:
        logging.info(f"Routing to image generation for model: {model_identifier}")
        if "llmrouter_images" not in clients:
            return jsonify({"error": "LLMRouter image client not configured."}), 500

        try:
            size = data.get('size', '1024x1024')
            quality = data.get('quality', 'auto')
            n = data.get('n', 1)

            image_client = clients["llmrouter_images"]
            response = image_client.images.generate(
                model=model_identifier,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )

            # Return as JSON with image data
            result = {
                "created": response.created,
                "data": [{"b64_json": getattr(img, 'b64_json', None), "url": getattr(img, 'url', None), "revised_prompt": getattr(img, 'revised_prompt', None)} for img in response.data]
            }
            return jsonify(result)
        except Exception as e:
            logging.error(f"Image generation error: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    # Handle base64 image - convert to data URL format
    if image and isinstance(image, dict) and 'data' in image:
        image_type = image.get('type', 'image/png')
        image_data = image.get('data')
        # Create data URL from base64
        data_url = f"data:{image_type};base64,{image_data}"
        images = images or []
        images.append(data_url)
        logging.info(f"Converted base64 image to data URL ({image_type})")

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
            return Response(output, mimetype=detect_mimetype(output))
        else: # All other providers go through the LLM Router
            if "llmrouter" not in clients:
                return jsonify({"error": "LLMRouter client not configured."}), 500
            router_client = clients["llmrouter"]
            message_content = build_message_content(prompt, images, provider)
            # Claude requires max_tokens parameter
            extra_params = {"max_tokens": 4096} if provider == "anthropic" else {}
            chat_completion = router_client.chat.completions.create(
                messages=[{"role": "user", "content": message_content}],
                model=model_identifier, # Pass the full identifier to the router
                **extra_params
            )
            output = chat_completion.choices[0].message.content
            return Response(output, mimetype=detect_mimetype(output))

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/images/generations', methods=['POST'])
def generate_image():
    """
    Generate images using gpt-image-1 or gpt-image-1-mini models.

    Request body:
    - model: "gpt-image-1" or "gpt-image-1-mini"
    - prompt: Text description of the image to generate
    - size: Image size (e.g., "1024x1024", "1536x1024", "1024x1536")
    - quality: "low", "medium", "high", or "auto" (default: "auto")
    - n: Number of images to generate (default: 1)
    """
    data = request.get_json()
    logging.info(f"Image generation request: {data}")

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    prompt = data.get('prompt')
    model = data.get('model', 'gpt-image-1')
    size = data.get('size', '1024x1024')
    quality = data.get('quality', 'auto')
    n = data.get('n', 1)

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    if "llmrouter_images" not in clients:
        return jsonify({"error": "LLMRouter image client not configured."}), 500

    try:
        image_client = clients["llmrouter_images"]
        response = image_client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n
        )

        # Return the response in OpenAI-compatible format
        result = {
            "created": response.created,
            "data": [{"b64_json": getattr(img, 'b64_json', None), "url": getattr(img, 'url', None), "revised_prompt": getattr(img, 'revised_prompt', None)} for img in response.data]
        }
        return jsonify(result)

    except Exception as e:
        logging.error(f"Image generation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8082))
    app.run(host='0.0.0.0', port=port)