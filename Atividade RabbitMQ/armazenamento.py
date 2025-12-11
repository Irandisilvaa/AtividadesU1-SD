import pika
import json
import base64
import os
import sys

# --- CONFIGURAÇÃO EXPLICITA GUEST/GUEST ---
CREDENTIALS = pika.PlainCredentials('guest', 'guest')
PARAMS = pika.ConnectionParameters(host='localhost', credentials=CREDENTIALS)

def callback(ch, method, properties, body, pasta_destino):
    payload = json.loads(body)
    nome = payload['nome_original']
    dados = payload['dados']

    caminho_final = os.path.join(pasta_destino, nome)

    with open(caminho_final, "wb") as fh:
        fh.write(base64.b64decode(dados))
    
    print(f" [x] Imagem salva em '{pasta_destino}': {nome}")

def main():
    # Define a pasta de destino via argumento
    pasta_destino = sys.argv[1] if len(sys.argv) > 1 else "storage_padrao"

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    connection = pika.BlockingConnection(PARAMS)
    channel = connection.channel()

    # Declara a exchange Fanout (Onde os conversores mandam)
    channel.exchange_declare(exchange='exchange_armazenamento', exchange_type='fanout')

    # Cria uma fila temporária e exclusiva para ESTA instância do servidor.
    # Assim, cada servidor tem sua própria fila recebendo cópias da exchange.
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Conecta a fila temporária na Exchange
    channel.queue_bind(exchange='exchange_armazenamento', queue=queue_name)

    print(f" [*] Servidor de Armazenamento iniciado na pasta: '{pasta_destino}'")

    # Configura o consumo passando a pasta de destino
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, pasta_destino),
        auto_ack=True
    )

    channel.start_consuming()

if __name__ == '__main__':
    main()