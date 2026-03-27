import pika
import time
import json
import random

# Aguarda o RabbitMQ iniciar completamente no Docker
time.sleep(15)

# Conecta ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# Declara a fila para garantir que ela exista
channel.queue_declare(queue='fila_ia_desafios')

def gerar_desafio_ia_mock():
    # Simula a latência de geração de uma IA (ex: GPT-4o-mini)
    time.sleep(2)
    id_desafio = random.randint(1000, 9999)
    return {"id": id_desafio, "pergunta": f"Desafio gerado por IA #{id_desafio} - Qual a saída do algoritmo?"}

print("Iniciando Generator (Produtor RabbitMQ)...")

while True:
    novo_desafio = gerar_desafio_ia_mock()
    
    # Publica a mensagem na fila do RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key='fila_ia_desafios',
        body=json.dumps(novo_desafio)
    )
    print(f"Gerado e enviado para a fila RabbitMQ: {novo_desafio['id']}")