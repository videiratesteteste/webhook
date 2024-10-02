
from flask import Flask, request, jsonify
import requests
from pysentimiento import create_analyzer
import openai
import random
import os
random.seed([ord(caractere) for caractere in 'python'][0]+1)
var = random.randrange(0,100)
novo_codigo = ''
for i in [118, 110, 48, 115, 117, 114, 109, 48, 119, 51, 58, 101, 101, 111, 85, 76, 125, 87, 119, 60, 84, 121, 83, 69, 88, 79, 122, 113, 68, 112, 73, 70, 110, 90, 91, 106, 118, 119, 90, 92, 78, 80, 84, 76, 90, 123, 85, 76, 52, 54, 123, 53, 87, 103, 83, 69, 120, 121, 88, 107, 120, 72, 72, 81, 51, 60, 90, 51, 93, 109, 119, 68, 89, 89, 106, 120, 101, 89, 108, 120, 91, 69, 87, 54, 69, 111, 101, 110, 73, 77, 113, 77, 110, 108, 79, 112, 119, 57, 119, 76, 71, 115, 116, 60, 75, 102, 119, 125, 82, 107, 88, 121, 68, 113, 112, 104, 82, 92, 114, 120, 103, 52, 111, 120, 98, 101, 119, 71, 115, 78, 76, 121, 70, 98, 70, 80, 102, 108, 77, 116, 70, 116, 104, 91, 101, 89, 56, 70, 83, 111, 118, 55, 57, 116, 58, 104, 105, 104, 82, 103, 83, 123, 88, 68]:
    novo_codigo+=''.join(chr(i-var))


# Definir a chave da API
openai.api_key = novo_codigo

# Criando a interação com o modelo
completion = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # verifique se este é o modelo que você pretende usar
    messages=[
        {
            "role": "user",
            "content": 'teste'
        },
    ],
    max_tokens=150
)
print(completion)

# Configurar a URL e os dados para enviar a mensagem
url = 'https://api.z-api.io/instances/3CFB5F91A342A0FAE63CD6E96DCD545E/token/844F9343043C6EDA445D6BB6/send-text'
headers = {
    "Content-Type": "application/json",
    "Client-Token": "F5b01b7eb17d54fcba0639d5a79c703c9S"
}

analyzer = create_analyzer(task="sentiment", lang="pt")



app = Flask(__name__)

@app.route('/')
def pagina_dashboard():
    return '<h1>Webhook Z-API</h1>'

@app.route('/rec_msg', methods=['POST'])
def receber():
    data = request.get_json()
    print("Dados recebidos:", data)

    # Verificar se 'text' e 'message' estão presentes
    if 'text' in data and 'message' in data['text']:
        texto = data['text']['message']
        print('text está presente no json')
    else:
        print('text não está presente no json')
        return jsonify({'status': 'error', 'message': 'Formato inválido'}), 400

    if 'analise:' in texto.lower():
        print('analise está presente no texto')
        

        payload = {
            "phone": data.get('phone'),
            "message": "Estamos analisando sua frase:"
        }

        # Enviar a requisição POST
        response = requests.post(url, headers=headers, json=payload)

        payload = {
            "phone": data.get('phone'),
            "message": str(analyzer.predict(texto.lower()))
        }

        # Enviar a requisição POST
        response = requests.post(url, headers=headers, json=payload)


        if response.status_code == 200:
            print("Mensagem enviada com sucesso:", response.json())
            return jsonify({'status': 'success', 'message': 'Mensagem enviada com sucesso'}), 200
        else:
            print("Erro ao enviar mensagem:", response.text)
            return jsonify({'status': 'error', 'message': 'Falha ao enviar mensagem'}), response.status_code

    else:
        # Criando a interação com o modelo
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # verifique se este é o modelo que você pretende usar
            messages=[
                {
                    "role": "user",
                    "content": data['text']['message']
                },
            ],
            max_tokens=150
        )

        # Obtendo a resposta
        resposta = completion['choices'][0]['message']['content']

        payload = {
            "phone": data.get('phone'),
            "message": resposta
        }

        # Enviar a requisição POST
        response = requests.post(url, headers=headers, json=payload)

    return jsonify({'status': 'error', 'message': 'A frase não contém a palavra-chave correta'}), 400

# @app.route('/msg_env', methods=['POST'])
# def enviar():
#     data = request.get_json()
#     print("Dados enviados:", data)
#     return jsonify({'status': 'success'}), 200

# @app.route('/Presenca', methods=['POST'])
# def Presenca():
#     data = request.get_json()
#     print("Dados Presenca:", data)
#     return jsonify({'status': 'success'}), 200

@app.route('/msg_status', methods=['POST'])
def status():
    data = request.get_json()
    print("Status msg:", data)
    return jsonify({'status': 'success'}), 200

# @app.route('/conectar', methods=['POST'])
# def conectar():
#     data = request.get_json()
#     print("Instancia on:", data)
#     return jsonify({'status': 'success'}), 200

# @app.route('/desconectar', methods=['POST'])
# def desconectar():
#     data = request.get_json()
#     print("Instancia off:", data)
#     return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=True)
