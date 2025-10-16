# Arquivo: server.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os

app = Flask(__name__)
# Habilita CORS para permitir que o Front-end local (ditadoColorido.html) acesse o servidor Python
CORS(app)

# Nome do arquivo de armazenamento
DATA_FILE = 'frases.json'

# --- Funções Auxiliares para Manipulação de Arquivo ---


def load_data():
    """Carrega dados do arquivo frases.json"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_data(data):
    """Salva dados no arquivo frases.json"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False

# --- Rotas da API ---


@app.route('/salvar_palavras', methods=['POST'])
def salvar_palavras():
    """Endpoint para receber e salvar as palavras do Front-end."""
    try:
        data = request.get_json()
        if not data or 'phrases' not in data:
            return jsonify({"success": False, "message": "Dados inválidos."}), 400

        phrases_to_save = data['phrases']

        # O Front-end deve enviar 6 frases (listas de 5 palavras)
        if not (isinstance(phrases_to_save, list) and len(phrases_to_save) == 6):
            return jsonify({"success": False, "message": "Formato de frase incorreto (esperado 6 listas)."}), 400

        # Salva a nova lista completa de frases
        if save_data(phrases_to_save):
            return jsonify({"success": True, "message": f"{len(phrases_to_save)} frases salvas com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Erro interno ao salvar no arquivo."}), 500

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro inesperado: {str(e)}"}), 500


@app.route('/carregar_palavras', methods=['GET'])
def carregar_palavras():
    """Endpoint para enviar as palavras salvas para o Front-end."""
    try:
        phrases = load_data()

        # Retorna a lista de frases. Se vazia, o Front-end usará as frases padrão.
        return jsonify({"success": True, "phrases": phrases})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro inesperado: {str(e)}"}), 500

# Rota para servir o arquivo HTML principal (opcional, mas recomendado)


@app.route('/')
def serve_game():
    return send_file('ditadoColorido.html')


if __name__ == '__main__':
    # Cria o arquivo de dados se ele não existir
    if not os.path.exists(DATA_FILE):
        save_data([])  # Salva uma lista vazia inicial

    # Roda o servidor na porta 5000
    print("Servidor Flask rodando em: http://127.0.0.1:5000")
    app.run(port=5000)
