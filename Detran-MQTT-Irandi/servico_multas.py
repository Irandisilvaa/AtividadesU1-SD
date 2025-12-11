import paho.mqtt.client as mqtt
import json
import banco

BROKER = "localhost"
CLIENT_ID = "servico_multas"
TOP_MULTA = "multas/lancar"

def publish(topic, payload):
    client.publish(topic, json.dumps(payload, ensure_ascii=False))

def on_connect(client, userdata, flags, reason_code, properties):
    print("[MULTAS] Serviço ativo.")
    client.subscribe(TOP_MULTA)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        # CORREÇÃO: A função salvar_multa recebe 4 argumentos, não 5.
        # O CPF é descoberto internamente pelo banco.py usando a placa.
        ok = banco.salvar_multa(
            data["ano"],
            data["descricao"],
            data["pontos"],
            data["placa"]
        )

        publish("resposta/multas/lancar", {"status": "ok" if ok else "erro"})
    except Exception as e:
        print(f"[ERRO] {e}")
        publish("resposta/multas/lancar", {"status": "erro", "msg": str(e)})

if __name__ == "__main__":
    # Garante que as tabelas existem antes de rodar
    banco.criar_tabelas()
    
    client = mqtt.Client(
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER, 1883)
        client.loop_forever()
    except ConnectionRefusedError:
        print("Não foi possível conectar ao Broker MQTT. Verifique se ele está rodando.")