import pika
import json
import base64
import io
import time
from PIL import Image

CREDENTIALS = pika.PlainCredentials('guest', 'guest')
PARAMS = pika.ConnectionParameters(host='localhost', credentials=CREDENTIALS)

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        nome = payload['nome_original']
        print(f" [.] Convertendo imagem: {nome}")

        # 1. Decodifica Base64
        img_bytes = base64.b64decode(payload['dados'])
        img = Image.open(io.BytesIO(img_bytes))

        # 2. Converte para Escala de Cinza ('L')
        img_gray = img.convert('L')

        # 3. Codifica de volta para Base64
        buffer = io.BytesIO()
        # Preserva o formato original ou usa JPEG
        fmt = img.format if img.format else 'JPEG'
        img_gray.save(buffer, format=fmt)
        img_gray_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # 4. Prepara mensagem para armazenamento
        nova_mensagem = {
            'nome_original': nome,
            'dados': img_gray_b64
        }

        # 5. Envia para a EXCHANGE (Fanout) para garantir redundância e todos os servidores de armazenamento conectados receberão cópia
        ch.basic_publish(
            exchange='exchange_armazenamento',
            routing_key='',
            body=json.dumps(nova_mensagem)
        )

        print(f" [x] Convertida e despachada: {nome}")
        
        # Confirma que processou a imagem
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f" [!] Erro no processamento: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(PARAMS)
    channel = connection.channel()

    # Garante que a fila de entrada existe
    channel.queue_declare(queue='fila_imagens_cruas', durable=True)
    
    # Garante que a Exchange de saída existe
    channel.exchange_declare(exchange='exchange_armazenamento', exchange_type='fanout')

    # QoS: Não manda outra mensagem enquanto eu não processar a atual
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='fila_imagens_cruas', on_message_callback=callback)

    print(' [*] Conversor de Imagens rodando. Aguardando...')
    channel.start_consuming()

if __name__ == '__main__':
    main()