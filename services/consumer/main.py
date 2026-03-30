from fastapi import FastAPI
import redis
import pika
import json
import random
import threading
import time

app = FastAPI()

#conexão com o Redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

#banco estático de Fallback
BANCO_ESTATICO_FALLBACK = [
    {"id": 1, "pergunta": "Qual era a cor do balão no comercial da que você acabou de assistir? (Fallback)"},
    {"id": 2, "pergunta": "Qual a marca da bebida exibida no último vídeo? (Fallback)"},
    {"id": 3, "pergunta": "No anúncio anterior, qual era o animal da marca que apareceu na tela? (Fallback)"},
    {"id": 4, "pergunta": "Quantos personagens estavam presentes no cenário principal do comercial? (Fallback)"},
    {"id": 5, "pergunta": "Qual foi o slogan falado no final do vídeo publicitário? (Fallback)"},
    {"id": 6, "pergunta": "O vídeo promocional mostrava um ambiente de praia ou de montanha? (Fallback)"},
    {"id": 7, "pergunta": "Qual aplicativo o anúncio convidava você a baixar? (Fallback)"}
]
def escutar_rabbitmq_e_alimentar_redis():
    """Roda em background para mover itens da Fila (RabbitMQ) para o Cache (Redis)"""
    time.sleep(20) #aguarda os serviços subirem
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='fila_ia_desafios')

    def callback(ch, method, properties, body):
        desafio = json.loads(body)
        #salva o desafio recebido da fila no topo do Pool do Redis
        r.lpush('pool_desafios', json.dumps(desafio))
        
        #mantém o Pool com no máximo 20 itens para não estourar a memória
        r.ltrim('pool_desafios', 0, 19)
        print(f"Consumido do RabbitMQ e guardado no Redis: {desafio['id']}")

    channel.basic_consume(queue='fila_ia_desafios', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

#assim que a API iniciar, começa a escutar o RabbitMQ em segundo plano
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=escutar_rabbitmq_e_alimentar_redis, daemon=True)
    thread.start()

@app.get("/desafio")
def obter_desafio():
    try:
        #tenta pegar um desafio do Pool (Redis) instantaneamente
        desafio_json = r.rpop('pool_desafios')
        
        if desafio_json:
            return {"origem": "Pool_Redis (Gerado via RabbitMQ)", "desafio": json.loads(desafio_json)}
        else:
            #Fallback 1: O Pool está vazio - IA não deu retorno
            return {"origem": "Fallback_Estatico (Pool Vazio)", "desafio": random.choice(BANCO_ESTATICO_FALLBACK)}
            
    except redis.exceptions.ConnectionError:
        # Fallback 2: O próprio Redis caiu
        return {"origem": "Fallback_Estatico (Sistema de Cache Fora do Ar)", "desafio": random.choice(BANCO_ESTATICO_FALLBACK)}