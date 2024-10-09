from flask import Flask, request, jsonify
import requests
from openai import OpenAI
import random
import os
import pymongo
import re
import json


# Definir a chave da API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
token=os.getenv("TOKEN")
instan=os.getenv("INSTANCIA")
token_head=os.getenv("Client_Token")

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

    # Verificar o tipo de 'audio' antes de processar
    audio_content = data.get('audio', None)

    if audio_content:

      # Baixar o arquivo de áudio
      audio_url = data['audio']['audioUrl']
      audio_response = requests.get(audio_url)

      # Salvar o arquivo de áudio localmente
      audio_file_path = 'audio.ogg'
      with open(audio_file_path, 'wb') as audio_file:
          audio_file.write(audio_response.content)

      # Transcrever o áudio em português
      with open(audio_file_path, "rb") as audio_file:
          transcript = client.audio.transcriptions.create(
              model="whisper-1",
              file=audio_file,
              language="pt"  # Definir o idioma como português
          )


      # Exibir a transcrição
      print('texto do audio: ',transcript.text)

      data.pop('audio')
      data['text']= {'message': transcript.text}

      print('deu certo a conversao')


    print("Dados recebidos:", data)

    telefone = data["phone"]

    # Conectar ao MongoDB
    BD_mongo = pymongo.MongoClient(os.getenv("STR_MONGO"))


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

    import time 

    time.sleep(10)


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

        print(tool.function.name)
        print(tool.function.arguments)

        url = 'https://api-dados-wf72.onrender.com/buscar_cliente'
        headers = {"Content-Type": "application/json"}
        data = tool.function.arguments

        # Realizar a requisição
        response = requests.get(url=url, data=data, headers=headers)

        # Converter a resposta JSON em um dicionário Python
        response_json = response.json()

        # Decodificar o campo 'body' da resposta
        body_content = response_json.get('body', None)

        if body_content:
            # Decodificar a string JSON para um objeto Python
            decoded_body = json.loads(body_content)  # Decodifica corretamente o conteúdo
            print(decoded_body)  # Agora você pode acessar os dados corretamente
        else:
            print("Chave 'body' não encontrada na resposta.")


      # de acordo com o metodo identificado envio o retorno do metodo
      if decoded_body:
        try:
          run = client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=[{"tool_call_id": tool.id,
                          "output": str(decoded_body)}]
          )
          print("retorno enviado com sucesso")
        except Exception as e:
          print("falha ao enviar o retorno:", e)
      else:
        print("sem saida para envio do retorno")
      
      time.sleep(10)
      if run.status == 'completed':
        print('run status completo')
        messages = client.beta.threads.messages.list(
          thread_id=thread.id
        )
      else:
        print('status ainda não é completo: ',run.status)

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
