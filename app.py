from flask import Flask, request, jsonify, render_template, send_from_directory, Response, stream_with_context
import requests
import json
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        user_message = request.args.get('message')
    else:
        user_message = request.json.get('message')

    payload = {
        "model": "gwen",  # Change model to "gwen"
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    def generate():
        try:
            with requests.post('http://localhost:11434/api/chat', json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        response_data = json.loads(line)
                        content = response_data.get('message', {}).get('content', '')
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
        except requests.exceptions.RequestException as req_err:
            print(f"RequestException: {req_err}")
            yield f"data: {json.dumps({'error': 'Request failed', 'details': str(req_err)})}\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
