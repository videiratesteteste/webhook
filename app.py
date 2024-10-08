from flask import Flask, request, jsonify
import requests
from openai import OpenAI
import random
import os
import pymongo
import re
import json

random.seed([ord(caractere) for caractere in 'python'][0]+1)
var = random.randrange(0,100)
novo_codigo = ''
for i in [118, 110, 48, 115, 117, 114, 109, 48, 119, 51, 58, 101, 101, 111, 85, 76, 125, 87, 119, 60, 84, 121, 83, 69, 88, 79, 122, 113, 68, 112, 73, 70, 110, 90, 91, 106, 118, 119, 90, 92, 78, 80, 84, 76, 90, 123, 85, 76, 52, 54, 123, 53, 87, 103, 83, 69, 120, 121, 88, 107, 120, 72, 72, 81, 51, 60, 90, 51, 93, 109, 119, 68, 89, 89, 106, 120, 101, 89, 108, 120, 91, 69, 87, 54, 69, 111, 101, 110, 73, 77, 113, 77, 110, 108, 79, 112, 119, 57, 119, 76, 71, 115, 116, 60, 75, 102, 119, 125, 82, 107, 88, 121, 68, 113, 112, 104, 82, 92, 114, 120, 103, 52, 111, 120, 98, 101, 119, 71, 115, 78, 76, 121, 70, 98, 70, 80, 102, 108, 77, 116, 70, 116, 104, 91, 101, 89, 56, 70, 83, 111, 118, 55, 57, 116, 58, 104, 105, 104, 82, 103, 83, 123, 88, 68]:
    novo_codigo+=''.join(chr(i-var))


instan = ''
for i in [54, 70, 73, 69, 56, 73, 60, 52, 68, 54, 55, 53, 68, 51, 73, 68, 72, 57, 54, 70, 71, 57, 72, 60, 57, 71, 70, 71, 56, 55, 56, 72]:
    instan+=''.join(chr(i-var))

token = ''
for i in [59, 55, 55, 73, 60, 54, 55, 54, 51, 55, 54, 70, 57, 72, 71, 68, 55, 55, 56, 71, 57, 69, 69, 57]:
    token+=''.join(chr(i-var))

token_head = ''
for i in [73, 56, 101, 51, 52, 101, 58, 104, 101, 52, 58, 103, 56, 55, 105, 102, 101, 100, 51, 57, 54, 60, 103, 56, 100, 58, 60, 102, 58, 51, 54, 102, 60, 86]:
    token_head+=''.join(chr(i-var))

# Definir a chave da API
client = OpenAI(api_key=novo_codigo)


# Configurar a URL e os dados para enviar a mensagem
url = f'https://api.z-api.io/instances/{instan}/token/{token}/send-text'
headers = {
    "Content-Type": "application/json",
    "Client-Token": token_head
}

app = Flask(__name__)

@app.route('/')
def pagina_dashboard():
    return '<h1>Webhook Z-API</h1>'

@app.route('/rec_msg', methods=['POST'])
def receber():
    data = request.get_json()
    print("Dados recebidos:", data)

    telefone = data["phone"]

    # Conectar ao MongoDB
    BD_mongo = pymongo.MongoClient('mongodb://mongo:ByLIFOINXzCqBohFiphXXrHxWDgAUBgV@junction.proxy.rlwy.net:13265')


    # Selecionar ou criar um banco de dados
    db = BD_mongo["Chatbot"]

    # Criar uma coleção (tabela)
    collection = db["Conversas"]

    # identifica se ja tem o cliente no banco de dados, nao tiver ele cria um historico para o cliente, caso tenha apenas agrega a nova mensagem ao historico
    if len(collection.find({"phone": data["phone"]}).distinct("phone")) == 0:
        conversa = {
            "phone": data["phone"],
            "messagens" : [
                {
                "role" : "user",
                "content" : data['text']['message']
                }
        ]}

        # Inserir um documento (registro) na coleção
        resultado = collection.insert_one(conversa)    
        
        print(f'Documento inserido com o ID: {resultado.inserted_id}')

    else:
        conversas = [conversa for conversa in collection.find({"phone": data["phone"]})][0]

        conversas['messagens'].extend([
                    {
                    "role" : "user",
                    "content" : data['text']['message']
                    }]
            )
        # Atualizando o documento com a lista de mensagens correta
        collection.update_one(
            {"phone": data["phone"]},  # Filtro para encontrar o documento
            {"$set": {"messagens": conversas['messagens']}}  # Atualizar a chave "mensagens"
        )

    
    # extrai os dados concatenados
    conversas = [conversa for conversa in collection.find({"phone": data["phone"]})][0]


    if len(conversas['messagens']) > 32:
        # Crie um thread (historico da mensagem)  e anexe o arquivo à mensagem
        thread = client.beta.threads.create(
        messages=conversas['messagens'][-32:]
        )
        
    else:
        # Crie um thread (historico da mensagem)  e anexe o arquivo à mensagem
        thread = client.beta.threads.create(
        messages=conversas['messagens']
        )


    # Use o auxiliar create_and_poll para criar uma execução e pesquisar o status da execução até que esteja em um estado terminal.
    run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id="asst_Qc2kUpoSzyLUYiTZHqeKhVMY",
    )
    
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(messages)
    else:
        print(run.status)
        print('erro')
        

    if run.required_action != None:

      # interage com a ultima pergunta do usuario
      tool = run.required_action.submit_tool_outputs.tool_calls[-1]

      if tool.function.name == "buscar_documento_data":
        url = 'https://api-dados-wf72.onrender.com/buscar_cliente'
        headers = {"Content-Type": "application/json"}
        data = tool.function.arguments

        # Realizar a requisição
        response = requests.get(url=url, data=data, headers=headers)

        # Converter a resposta JSON em um dicionário Python
        response_json = response.json()

        # Verificar o tipo de 'body' antes de processar
        body_content = response_json.get('body', None)

        if body_content:

          decoded_body = json.loads(body_content)
          print(decoded_body)  # Conteúdo decodificado corretamente

        else:
          print("Chave 'body' não encontrada na resposta.")


      # Submit all tool outputs at once after collecting them in a list
      if decoded_body:
        try:
          run = client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
      
            tool_outputs=[{"tool_call_id": tool.id,
                          "output": str(decoded_body)}]
          )
          print("Tool outputs submitted successfully.")
        except Exception as e:
          print("Failed to submit tool outputs:", e)
      else:
        print("No tool outputs to submit.")
    
      if run.status == 'completed':
        messages = client.beta.threads.messages.list(
          thread_id=thread.id
        )
      else:
        print(run.status)

      resposta = messages.data[0].content[0].text.value
      print(resposta)

    else:
      print('nenhum metodo aplicado')
      resposta = messages.data[0].content[0].text.value
      print(resposta)
      
    conversas['messagens'].append({"role": "assistant", "content": resposta})

    # Atualizando o documento com a lista de mensagens correta
    collection.update_one(
        {"phone": telefone},  # Filtro para encontrar o documento
        {"$set": {"messagens": conversas['messagens']}}  # Atualizar a chave "mensagens"
    )


    payload = {
        "phone": telefone,
        "message": resposta
    }

    # Configurar a URL e os dados para enviar a mensagem
    url = f'https://api.z-api.io/instances/{instan}/token/{token}/send-text'
    headers = {
        "Content-Type": "application/json",
        "Client-Token": token_head
    }

    # Enviar a requisição POST
    response = requests.post(url, headers=headers, json=payload)

    print(response)

    return response,200

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
