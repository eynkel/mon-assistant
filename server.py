import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

api_key = os.environ.get('OPENROUTER_API_KEY')
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    file_content = data.get('file_content', None)
    file_name = data.get('file_name', None)

    system_msg = {
        'role': 'system',
        'content': "Tu es un assistant IA utile et concis. Réponds en français si l'utilisateur écrit en français."
    }

    full_messages = [system_msg]
    for msg in messages:
        content = msg['content']
        if msg.get('file_name'):
            content += f"\n\n[Pièce jointe: {msg['file_name']}]"
        full_messages.append({'role': msg['role'], 'content': content})

    if file_content:
        full_messages.append({'role': 'system', 'content': f"[Fichier uploadé: {file_name}] Contenu base64: {file_content}"})

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=full_messages,
        max_tokens=4096,
    )

    return jsonify({
        'reply': response.choices[0].message.content
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)