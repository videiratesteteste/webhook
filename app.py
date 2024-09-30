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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=True)
