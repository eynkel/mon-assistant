import os
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_client():
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY non définie")
    return openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

@app.route('/')
def index():
    path = os.path.join(BASE_DIR, 'index.html')
    return send_file(path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
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

    if file_name:
        full_messages.append({'role': 'system', 'content': f"[Fichier uploadé: {file_name}]"})

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=full_messages,
            max_tokens=4096,
        )
        return jsonify({'reply': response.choices[0].message.content})
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return jsonify({'reply': f"Erreur: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Démarrage sur port {port}")
    app.run(host='0.0.0.0', port=port)