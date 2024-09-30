from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def pagina_dashboard():

    return '<h1>Webhook Z-API</h1>'


@app.route('/rec_msg', methods=['POST'])
def webhook():
    # Captura os dados do webhook
    data = request.get_json()

    # Aqui você pode processar os dados recebidos
    print("Dados recebidos:", data)

    # Retorne uma resposta
    return jsonify({'status': 'success'}), 200

def run_app():

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)


run_app()