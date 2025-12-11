import pika
import sys
import os
import json
import base64

CREDENTIALS = pika.PlainCredentials('guest', 'guest')
PARAMS = pika.ConnectionParameters(host='localhost', credentials=CREDENTIALS)

def main():
    # Pega o nome da pasta dos argumentos e se não passar nada, usa 'cliente_padrao'
    pasta_origem = sys.argv[1] if len(sys.argv) > 1 else "cliente_padrao"

    # Cria a pasta se não existir 
    if not os.path.exists(pasta_origem):
        os.makedirs(pasta_origem)
        print(f"[!] A pasta '{pasta_origem}' foi criada. Coloque imagens nela e rode novamente.")
        return

    # Conexão
    connection = pika.BlockingConnection(PARAMS)
    channel = connection.channel()

    # Declara a fila de tarefas 
    channel.queue_declare(queue='fila_imagens_cruas', durable=True)

    arquivos = os.listdir(pasta_origem)
    enviados = 0

    print(f"[*] Cliente lendo da pasta: '{pasta_origem}'")

    for nome_arquivo in arquivos:
        if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            caminho_completo = os.path.join(pasta_origem, nome_arquivo)
            
            # Converte imagem para Base64
            with open(caminho_completo, "rb") as image_file:
                dados_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            mensagem = {
                'nome_original': nome_arquivo,
                'dados': dados_base64
            }

            # Envia para a fila
            channel.basic_publish(
                exchange='',
                routing_key='fila_imagens_cruas',
                body=json.dumps(mensagem),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensagem persistente
                ))
            print(f" [x] Enviado '{nome_arquivo}'")
            enviados += 1

    if enviados == 0:
        print(f"[!] Nenhuma imagem encontrada em '{pasta_origem}'.")
    
    connection.close()

if __name__ == '__main__':
    main()