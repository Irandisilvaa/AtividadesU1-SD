[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=22003690)

# 🚗 Sistema DETRAN Distribuído (MQTT + Microsserviços)

Este projeto implementa um sistema para o DENATRAN utilizando arquitetura de **Microsserviços** comunicando-se via protocolo **MQTT**. O sistema gerencia condutores, veículos, multas e consultas através de serviços independentes e desacoplados.

## 📋 Funcionalidades
* Cadastro de Condutores.
* Emplacamento de Veículos e Cálculo de IPVA.
* Transferência de Propriedade.
* Lançamento de Multas (com verificação de dono).
* Consultas (Top 5 infratores, multas por ano, etc.).

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.11+
* **Comunicação:** Protocolo MQTT (Biblioteca `paho-mqtt`)
* **Broker:** Eclipse Mosquitto (via Docker)
* **Banco de Dados:** SQLite (Arquivo local `detran.db`)
* **Interface:** Linha de Comando (CLI) via `cliente.py`

---

## 🚀 Guia de Instalação e Execução

Siga os passos abaixo na ordem exata para garantir o funcionamento do ambiente distribuído.

### 1. Pré-requisitos
Certifique-se de ter instalado:
* [Python 3](https://www.python.org/downloads/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 2. Configuração do Python
Abra um terminal na pasta do projeto e instale a dependência do MQTT:

powershell: pip install paho-mqtt

### 3. Subindo o Broker MQTT (Docker)
Para que os microsserviços conversem entre si, precisamos do servidor MQTT (Mosquitto) rodando. Devido a políticas de segurança do Mosquitto, precisamos configurá-lo para aceitar conexões locais sem senha.

Execute os comandos abaixo no PowerShell (na pasta do projeto):

## Passo A: Criar arquivo de configuração
Este comando cria um arquivo mosquitto.conf configurado para liberar a porta 1883.
powershell: Set-Content -Path mosquitto.conf -Value "listener 1883`nallow_anonymous true"

## Passo B: Limpar containers antigos
powershell: docker rm -f mosquitto-detran
Passo C: Iniciar o servidor Mosquitto
powershell: docker run -d --name mosquitto-detran -p 1883:1883 -v "${PWD}/mosquitto.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto

Verificação
Rode: docker ps
Se o container mosquitto-detran estiver na lista, o servidor está pronto.

# se estiver em linux 

Bash: echo -e "listener 1883\nallow_anonymous true" > mosquitto.conf
Verificação: Digite ls -l e veja se aparece um arquivo mosquitto.conf (não pode ser azul/diretório).

Passo 3: Rodar o Docker
Bash: docker run -d --name mosquitto-detran -p 1883:1883 -v "$(pwd)/mosquitto.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto

Passo 4: Verificar
Digite: docker ps
Se aparecer na lista, está funcionando! Aí é só abrir os outros terminais e rodar os scripts Python (python servico_condutores.py, etc.).

### 4. Executando os Microsserviços (Back-end)
Como é um sistema distribuído, cada serviço deve rodar em seu próprio processo.
Você precisará abrir 4 Terminais (Janelas) separadas e manter todas abertas.

Terminal 1 (Serviço de Condutores)
powershell
python servico_condutores.py

Terminal 2 (Serviço de Veículos)
powershell
python servico_veiculos.py

Terminal 3 (Serviço de Multas)
powershell
python servico_multas.py

Terminal 4 (Serviço de Consultas)
powershell
python servico_consultas.py

Aguarde aparecer a mensagem de "Conectado" ou "Online" em cada terminal e deixe-os abertos.

### 5. Executando o Cliente 
Agora que toda a infraestrutura está rodando, abra um 5º Terminal para rodar o cliente que envia os comandos.

Terminal 5 (Cliente)
powershell
python cliente.py


## Roteiro de Teste (Exemplo de Uso)
Para testar o fluxo completo sem erros de integridade (Foreign Key), siga esta ordem no menu do cliente:

1️⃣ Opção 4 — Cadastrar Condutor
Cadastre uma pessoa:

CPF: 1
Nome: Jose

2️⃣ Opção 1 — Emplacar Veículo
Cadastre um carro para o CPF criado acima:

Placa: ABC-1234
CPF: 1

3️⃣ Opção 2 — Calcular IPVA
Consultar o IPVA da placa ABC-1234.

4️⃣ Opção 5 — Lançar Multa
Aplique uma multa para ABC-1234.
O sistema localizará automaticamente o CPF 1.

5️⃣ Opção 6 ou 7 — Consultas
Verifique se os dados foram salvos corretamente.

