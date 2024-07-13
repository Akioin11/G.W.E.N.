import json
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory, Response, stream_with_context

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
        payload = request.args.get('payload')
    else:
        payload = request.json.get('payload')

    def generate():
        try:
            with requests.post('http://localhost:11434/api/chat', json=json.loads(payload), stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        yield f"data: {line.decode('utf-8')}\n\n"
        except requests.exceptions.RequestException as req_err:
            print(f"RequestException: {req_err}")
            yield f"data: {json.dumps({'error': 'Request failed', 'details': str(req_err)})}\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
