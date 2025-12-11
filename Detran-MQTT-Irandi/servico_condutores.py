import paho.mqtt.client as mqtt
import json
import banco

BROKER = "localhost"
CLIENT_ID = "servico_condutores"

TOP_CADASTRO = "condutores/cadastro"

def publish(topic, payload):
    client.publish(topic, json.dumps(payload, ensure_ascii=False))

def on_connect(client, userdata, flags, reason_code, properties):
    print("[CONDUTORES] Conectado ao broker!")
    client.subscribe(TOP_CADASTRO)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    cpf = data.get("cpf")
    nome = data.get("nome")

    res = banco.salvar_condutor(cpf, nome)
    if res:
        publish("resposta/condutores/cadastro", {"status": "ok", "data": res})
    else:
        publish("resposta/condutores/cadastro", {"status": "erro", "msg": "CPF já existe"})

if __name__ == "__main__":
    banco.criar_tabelas()
    client = mqtt.Client(
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883)
    client.loop_forever()
