from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def pagina_dashboard():
    return '<h1>Webhook Z-API</h1>'

@app.route('/rec_msg', methods=['POST'])
def receber():
    data = request.get_json()
    print("Dados recebidos:", data)
    return jsonify({'status': 'success'}), 200

@app.route('/msg_env', methods=['POST'])
def enviar():
    data = request.get_json()
    print("Dados enviados:", data)
    return jsonify({'status': 'success'}), 200

@app.route('/Presenca', methods=['POST'])
def Presenca():
    data = request.get_json()
    print("Dados Presenca:", data)
    return jsonify({'status': 'success'}), 200

@app.route('/msg_status', methods=['POST'])
def status():
    data = request.get_json()
    print("Status msg:", data)
    return jsonify({'status': 'success'}), 200

@app.route('/conectar', methods=['POST'])
def conectar():
    data = request.get_json()
    print("Instancia on:", data)
    return jsonify({'status': 'success'}), 200

@app.route('/desconectar', methods=['POST'])
def desconectar():
    data = request.get_json()
    print("Instancia off:", data)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=True)
