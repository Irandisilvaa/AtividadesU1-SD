# Atividade 01 - Sistemas Distribuídos: Processamento de Imagens com RabbitMQ

**Disciplina:** Sistemas Distribuídos - Departamento de Computação
**Aluno:** Irandi Silva


## Descrição do Projeto

Este projeto implementa um módulo distribuído para conversão de imagens coloridas para tons de cinza, utilizando o modelo de fila de mensagens **RabbitMQ**. A arquitetura foi desenvolvida para atender aos seguintes requisitos:

1.  **Escalabilidade (Produtores e Conversores):** Múltiplos clientes podem enviar imagens e múltiplos conversores processam a fila de forma concorrente (Padrão *Work Queue*).
2.  **Redundância (Armazenamento):** Todos os servidores de armazenamento ativos recebem uma cópia de todas as imagens processadas para evitar perda de dados (Padrão *Publish/Subscribe - Fanout*).
3.  **Integridade:** As imagens convertidas mantêm o nome original do arquivo.


## Pré-requisitos e Instalação

### 1. Python e Bibliotecas
Certifique-se de ter o Python 3.x instalado. Instale as dependências do projeto:

bash: pip install pika Pillow

2. RabbitMQ (Configuração guest/guest): O código foi configurado hardcoded com o usuário guest e senha guest, conforme exigido no enunciado. A maneira mais fácil de rodar o RabbitMQ compatível é via Docker:

Bash: docker run -d --hostname my-rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
Nota: A imagem oficial do RabbitMQ já vem com o usuário guest configurado por padrão.

Como Executar o Sistema: Para demonstrar a escalabilidade e redundância, recomenda-se abrir múltiplos terminais e executar as instâncias na seguinte ordem:

Passo 1: Iniciar os Servidores de Armazenamento (Redundância)
Abra 2 terminais. Cada um simulará um servidor salvando em uma pasta diferente. Graças à exchange Fanout, ambos receberão as mesmas imagens.

Terminal 1 (Servidor A):
Bash: python armazenamento.py servidor_storage_A

Terminal 2 (Servidor B):
Bash: python armazenamento.py servidor_storage_B

Passo 2: Iniciar os Conversores (Escalabilidade): Abra 1 ou mais terminais para os workers. O RabbitMQ distribuirá as tarefas entre eles.

Terminal 3:
Bash: python conversor.py

Passo 3: Iniciar os Clientes (Produtores)
Crie pastas com imagens (ex: cliente_fotos_1) e execute o produtor apontando para elas.

Terminal 4:
Bash: python produtor.py cliente_fotos_1

(Opcional) Terminal 5 - Outro cliente:
Bash: python produtor.py cliente_fotos_2

Detalhes da Implementação
Autenticação: O código utiliza pika.PlainCredentials('guest', 'guest') em todos os módulos ou seja, não precisa estar colacando a senha manualmente

Topologia:
Cliente -> Fila fila_imagens_cruas.
Conversor -> Processa -> Exchange exchange_armazenamento (Tipo Fanout).
Armazenamento -> Cria fila temporária (exclusive=True) e conecta na Exchange.
