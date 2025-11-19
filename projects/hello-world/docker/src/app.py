from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/computation', methods=['POST'])
def computation():
    """
    Accepts a POST request with a JSON body containing an 'input' key.
    Returns a greeting message including the input value.
    """
    data = request.get_json()
    if not data or 'input' not in data:
        return jsonify({"error": "Missing 'input' in request body"}), 400

    user_input = data.get('input')
    return jsonify({"output": f"hello world, your input was: {user_input}"})

if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8081))
    app.run(host='0.0.0.0', port=port)