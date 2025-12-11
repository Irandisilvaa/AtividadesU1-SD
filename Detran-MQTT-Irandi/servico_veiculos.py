# servico_veiculos.py
import paho.mqtt.client as mqtt
import json
import banco

BROKER = "localhost"
CLIENT_ID = "servico_veiculos"

TOP_EMPLACAR = "veiculos/emplacar"
TOP_TRANSFERIR = "veiculos/transferir"
TOP_IPVA = "veiculos/ipva"

def publish(topic, payload):
    client.publish(topic, json.dumps(payload, ensure_ascii=False))

def on_connect(client, userdata, flags, reason_code, properties):
    print("[VEICULOS] Serviço online")
    client.subscribe([(TOP_EMPLACAR, 0), (TOP_TRANSFERIR,0), (TOP_IPVA,0)])

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    if msg.topic == TOP_EMPLACAR:
        ok = banco.emplacar(data["placa"], data["modelo"], data["valor"], data["cpf"], data["ano"])
        publish("resposta/veiculos/emplacar", {"status": "ok" if ok else "erro"})

    elif msg.topic == TOP_TRANSFERIR:
        ok = banco.transferir(data["placa"], data["cpf"])
        publish("resposta/veiculos/transferir", {"status": "ok" if ok else "erro"})

    elif msg.topic == TOP_IPVA:
        valor = banco.calcular_ipva(data["placa"])
        publish("resposta/veiculos/ipva", {"status": "ok", "ipva": valor})

if __name__ == "__main__":
    client = mqtt.Client(
        client_id=CLIENT_ID,
        # CORREÇÃO AQUI: Troque .V5 por .VERSION2
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883)
    client.loop_forever()
