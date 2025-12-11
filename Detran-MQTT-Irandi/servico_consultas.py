import sqlite3
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
CLIENT_ID = "servico_consultas"

DB = "detran.db"

def db():
    return sqlite3.connect(DB)

# -----------------------------
# MQTT CALLBACKS
# -----------------------------
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONSULTAS conectado ao broker MQTT.")

    client.subscribe("consultas/veiculos_ano")
    client.subscribe("consultas/multas_placa_ano")
    client.subscribe("consultas/multas_cpf_ano")
    client.subscribe("consultas/multas_ano")
    client.subscribe("consultas/top5")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except:
        payload = {}

    print(f"[CONSULTAS] Mensagem recebida em {msg.topic}: {payload}")

    if msg.topic == "consultas/veiculos_ano":
        resposta = consultar_veiculos_ano(payload.get("ano"))
        enviar("resposta/veiculos/ano", resposta)

    elif msg.topic == "consultas/multas_placa_ano":
        resposta = consultar_multas_placa_ano(payload.get("placa"), payload.get("ano"))
        enviar("resposta/multas/placa_ano", resposta)

    elif msg.topic == "consultas/multas_cpf_ano":
        resposta = consultar_multas_cpf_ano(payload.get("cpf"), payload.get("ano"))
        enviar("resposta/multas/cpf_ano", resposta)

    elif msg.topic == "consultas/multas_ano":
        resposta = consultar_multas_ano(payload.get("ano"))
        enviar("resposta/multas/ano", resposta)

    elif msg.topic == "consultas/top5":
        resposta = top5_condutores()
        enviar("resposta/multas/top5", resposta)


def enviar(topic, msg):
    client.publish(topic, json.dumps(msg, ensure_ascii=False))
    print(f"[CONSULTAS] Enviado → {topic}: {msg}")


# -----------------------------
# CONSULTAS
# -----------------------------
def consultar_veiculos_ano(ano):
    con = db(); cur = con.cursor()
    cur.execute("SELECT placa, modelo, valor, cpf, ano FROM veiculos WHERE ano = ?", (ano,))
    res = cur.fetchall()
    con.close()
    return {"status": "ok", "resultados": res}


def consultar_multas_placa_ano(placa, ano):
    con = db(); cur = con.cursor()
    cur.execute(
        "SELECT descricao, pontos, ano, cpf FROM multas WHERE placa = ? AND ano = ?",
        (placa, ano)
    )
    res = cur.fetchall()
    con.close()
    return {"status": "ok", "resultados": res}


def consultar_multas_cpf_ano(cpf, ano):
    con = db(); cur = con.cursor()
    cur.execute(
        "SELECT descricao, pontos, ano, placa FROM multas WHERE cpf = ? AND ano = ?",
        (cpf, ano)
    )
    res = cur.fetchall()
    con.close()
    return {"status": "ok", "resultados": res}


def consultar_multas_ano(ano):
    con = db(); cur = con.cursor()
    cur.execute("SELECT placa, cpf, descricao, pontos FROM multas WHERE ano = ?", (ano,))
    res = cur.fetchall()
    con.close()
    return {"status": "ok", "resultados": res}


def top5_condutores():
    con = db(); cur = con.cursor()
    cur.execute("""
        SELECT cpf, SUM(pontos) AS total
        FROM multas
        GROUP BY cpf
        ORDER BY total DESC
        LIMIT 5
    """)
    res = cur.fetchall()
    con.close()
    return {"status": "ok", "top5": res}


# -----------------------------
# MQTT CLIENT
# -----------------------------
client = mqtt.Client(
    client_id=CLIENT_ID,
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

if __name__ == "__main__":
    client.connect(BROKER, PORT, 60)
    print("Serviço de CONSULTAS iniciado...")
    client.loop_forever()
