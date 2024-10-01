from flask import Flask, request, jsonify
import requests
import json
# from pysentimiento import create_analyzer

# analyzer = create_analyzer(task="sentiment", lang="pt")

app = Flask(__name__)

@app.route('/')
def pagina_dashboard():
    return '<h1>Webhook Z-API</h1>'

@app.route('/rec_msg', methods=['POST'])
def receber():
    data = request.get_json()
    print("Dados recebidos:", data)
    print(type(data))

    # Verificar se 'text' e 'message' estão presentes
    if 'text' in data and 'message' in data['text']:
        texto = data['text']['message']
        print('text está presente no json')
    else:
       print('text n esta presente no json')
       return jsonify({'status': 'error', 'message': 'Formato inválido'}), 400 
    if 'analise:' in texto.lower():
        print('analise está presente no texto')
        # enviar msg

        url = 'https://api.z-api.io/instances/3CFB5F91A342A0FAE63CD6E96DCD545E/token/844F9343043C6EDA445D6BB6/send-text'

        data = {
            "phone": data['phone'],
            "message": "Estamos analisando sua frase:"
        }
        headers = {
            "Content-Type": "application/json",
            "Client-Token": "F5b01b7eb17d54fcba0639d5a79c703c9S"
        }

        response = requests.post(url, headers=headers, data=data)

        # message_parts = texto.split(':')
        # if len(message_parts) > 1:
        #     mensagem_para_analisar = message_parts[1].strip()
        # else:
        #     return jsonify({'status': 'error', 'message': 'Formato inválido'}), 400


        # resultado_analise = analyzer.predict(mensagem_para_analisar)
        # message = str(resultado_analise)  # Isso retornará 'POS', 'NEG' ou 'NEU'

        # data = {
        #     "phone": data['phone'],
        #     "message": message
        # }

        # headers = {
        #     "Content-Type": "application/json",
        #     "Client-Token": "F5b01b7eb17d54fcba0639d5a79c703c9S"
        # }

        # response = requests.post(url, headers=headers, data=data)

        # if response.status_code == 200:
        #     print(response.json())
    else:
        print('analise n esta presente no json')

    return jsonify({'status': 'success'}), 200

@app.route('/msg_env', methods=['POST'])
def enviar():
    data = request.get_json()
    print("Dados enviados:", data)
    return jsonify({'status': 'success'}), 200

# @app.route('/Presenca', methods=['POST'])
# def Presenca():
#     data = request.get_json()
#     print("Dados Presenca:", data)
#     return jsonify({'status': 'success'}), 200

# @app.route('/msg_status', methods=['POST'])
# def status():
#     data = request.get_json()
#     print("Status msg:", data)
#     return jsonify({'status': 'success'}), 200

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
