import paho.mqtt.client as mqtt
import json
import threading
import time
import sys
import os

BROKER = "localhost"
PORT = 1883
CLIENT_ID = "cliente_cli_1"

responses = {}

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("resposta/#")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except:
        payload = msg.payload.decode("utf-8")

    responses[msg.topic] = payload


def formatar_saida(dados):
    """Transforma o JSON feio em texto para o usuário"""
    print("\n" + "="*40)
    print("RESULTADO DA OPERAÇÃO")
    print("="*40)

    if not isinstance(dados, dict):
        print(f"Resposta bruta: {dados}")
        return

    # 1. Verifica Erros
    if dados.get("status") == "erro":
        print(f"OCORREU UM ERRO:")
        print(f"Mensagem: {dados.get('msg', 'Erro desconhecido')}")
        return

    # 2. Verifica Sucesso Genérico (só status ok)
    if len(dados) == 1 and dados.get("status") == "ok":
        print("Operação realizada com sucesso!")
        return

    # 3. Caso Cadastro (tem chave 'data')
    if "data" in dados:
        print("Cadastro realizado!")
        d = dados["data"]
        print(f"   Nome: {d.get('nome')} | CPF: {d.get('cpf')}")

    # 4. Caso do IPVA
    elif "ipva" in dados:
        print(f"💰 Valor do IPVA calculado:")
        print(f"   R$ {dados['ipva']:.2f}")

    # 5. Caso do Top 5 Condutores
    elif "top5" in dados:
        print("RANKING DE INFRATORES (TOP 5):")
        if not dados["top5"]:
            print("Nenhuma multa registrada.")
        for i, item in enumerate(dados["top5"], 1):
            # item é (cpf, total_pontos)
            print(f"   {i}º Lugar - CPF: {item[0]} | Pontos: {item[1]}")

    # 6. Caso Listas (Veículos ou Multas) - chave 'resultados'
    elif "resultados" in dados:
        lista = dados["resultados"]
        if not lista:
            print("A consulta não retornou nenhum registro.")
        else:
            print(f"Foram encontrados {len(lista)} registros:\n")
            for item in lista:
                linha_formatada = " | ".join(str(x) for x in item)
                print(f" {linha_formatada}")

    else:
        # Caso sobe alguma coisa que não foi tratada
        print(json.dumps(dados, indent=4, ensure_ascii=False))
    
    print("="*40)


client = mqtt.Client(
    client_id=CLIENT_ID,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

def start_client():
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT)
        threading.Thread(target=client.loop_forever, daemon=True).start()
        time.sleep(0.5)
    except Exception as e:
        print(f"Erro ao conectar no Broker: {e}")
        sys.exit(1)

def publish(topic, payload):
    client.publish(topic, json.dumps(payload, ensure_ascii=False))

def wait_response(request_topic_suffix, timeout=5):
    target_topic = "resposta/" + request_topic_suffix
    waited = 0
    
    # Limpa resposta antiga se houver (para não pegar o cache)
    if target_topic in responses:
        del responses[target_topic]

    while waited < timeout:
        if target_topic in responses:
            return responses.pop(target_topic)
        time.sleep(0.1)
        waited += 0.1
    
    return {"status": "erro", "msg": "Timeout - O serviço demorou para responder."}

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')



def menu():
    limpar_tela() 
    print("""

            SISTEMA DETRAN - MQTT
===========================================
1 - Emplacar veículo
2 - Calcular IPVA (2%)
3 - Transferir proprietário
4 - Cadastrar condutor
5 - Lançar multa
6 - Consultar veículos de um ano
7 - Consultar multas de um veículo em um ano
8 - Consultar multas de um condutor em um ano
9 - Consultar multas em um ano
10 - Top 5 condutores por pontuação
0 - Sair
===========================================
""")


def main_loop():
    while True:
        menu()
        opt = input("Digite a opção desejada: ").strip()

        if opt == "0":
            print("Saindo...")
            break

        resp = None # Variável para guardar a resposta

        # 1 - Emplacar
        if opt == "1":
            print("\n--- Emplacar Veículo ---")
            placa = input("Placa: ")
            modelo = input("Modelo: ")
            try:
                valor = float(input("Valor: "))
                cpf = input("CPF do condutor: ")
                ano = int(input("Ano: "))
                
                publish("veiculos/emplacar", {
                    "placa": placa, "modelo": modelo, "valor": valor, "cpf": cpf, "ano": ano
                })
                resp = wait_response("veiculos/emplacar")
            except ValueError:
                resp = {"status": "erro", "msg": "Valor ou Ano inválidos (use números)."}

        # 2 - IPVA
        elif opt == "2":
            print("\n--- Calcular IPVA ---")
            placa = input("Placa: ")
            publish("veiculos/ipva", {"placa": placa})
            resp = wait_response("veiculos/ipva")

        # 3 - Transferir
        elif opt == "3":
            print("\n--- Transferir Veículo ---")
            placa = input("Placa: ")
            cpf = input("CPF do novo dono: ")
            publish("veiculos/transferir", {"placa": placa, "cpf": cpf})
            resp = wait_response("veiculos/transferir")

        # 4 - Cadastrar condutor
        elif opt == "4":
            print("\n--- Novo Condutor ---")
            cpf = input("CPF: ")
            nome = input("Nome: ")
            publish("condutores/cadastro", {"cpf": cpf, "nome": nome})
            resp = wait_response("condutores/cadastro")

        # 5 - Multa
        elif opt == "5":
            print("\n--- Lançar Multa ---")
            try:
                placa = input("Placa: ")
                ano = int(input("Ano da infração: "))
                descricao = input("Descrição: ")
                pontos = int(input("Pontos: "))
                
                publish("multas/lancar", {
                    "ano": ano, "descricao": descricao, "pontos": pontos, "placa": placa
                })
                resp = wait_response("multas/lancar")
            except ValueError:
                resp = {"status": "erro", "msg": "Ano e Pontos devem ser números."}

        # 6 - Consulta veículos/ano
        elif opt == "6":
            try:
                print("\n--- Consulta Veículos por Ano ---")
                ano = int(input("Ano: "))
                publish("consultas/veiculos_ano", {"ano": ano})
                resp = wait_response("veiculos/ano")
            except ValueError:
                resp = {"status": "erro", "msg": "Ano inválido."}

        # 7 - consulta multas por placa
        elif opt == "7":
            try:
                print("\n--- Multas por Veículo ---")
                placa = input("Placa: ")
                ano = int(input("Ano: "))
                publish("consultas/multas_placa_ano", {"placa": placa, "ano": ano})
                resp = wait_response("multas/placa_ano")
            except ValueError:
                resp = {"status": "erro", "msg": "Ano inválido."}

        # 8 - multas por condutor
        elif opt == "8":
            try:
                print("\n--- Multas por Condutor ---")
                cpf = input("CPF: ")
                ano = int(input("Ano: "))
                publish("consultas/multas_cpf_ano", {"cpf": cpf, "ano": ano})
                resp = wait_response("multas/cpf_ano")
            except ValueError:
                resp = {"status": "erro", "msg": "Ano inválido."}

        # 9 - multas por ano
        elif opt == "9":
            try:
                print("\n--- Todas as Multas do Ano ---")
                ano = int(input("Ano: "))
                publish("consultas/multas_ano", {"ano": ano})
                resp = wait_response("multas/ano")
            except ValueError:
                resp = {"status": "erro", "msg": "Ano inválido."}

        # 10 - Top 5 Infratores
        elif opt == "10":
            print("\n--- Top 5 Infratores ---")
            publish("consultas/top5", {})
            resp = wait_response("multas/top5")

        else:
            print("Opção inválida.")

        if resp:
            formatar_saida(resp)
            input("\n[Pressione ENTER para voltar ao menu principal...]")

if __name__ == "__main__":
    start_client()
    print("Iniciando sistema...")
    time.sleep(1)
    main_loop()