import json
import os
import random
import threading
import time

from fastapi import FastAPI
import pika
import redis

app = FastAPI(title="IA como Pool API")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE", "fila_ia_desafios")
REDIS_POOL_KEY = os.environ.get("REDIS_POOL_KEY", "pool_desafios")
REDIS_MAX_ITEMS = int(os.environ.get("REDIS_MAX_ITEMS", "20"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

BANCO_ESTATICO_FALLBACK = [
    {"id": 1, "pergunta": "Qual era a cor do balão no comercial que você acabou de assistir? (Fallback)"},
    {"id": 2, "pergunta": "Qual a marca da bebida exibida no último vídeo? (Fallback)"},
    {"id": 3, "pergunta": "No anúncio anterior, qual era o animal da marca que apareceu na tela? (Fallback)"},
    {"id": 4, "pergunta": "Quantos personagens estavam presentes no cenário principal do comercial? (Fallback)"},
    {"id": 5, "pergunta": "Qual foi o slogan falado no final do vídeo publicitário? (Fallback)"},
    {"id": 6, "pergunta": "O vídeo promocional mostrava um ambiente de praia ou de montanha? (Fallback)"},
    {"id": 7, "pergunta": "Qual aplicativo o anúncio convidava você a baixar? (Fallback)"},
]


def aguardar_redis() -> None:
    """Verifica e aguarda a disponibilidade do banco Redis."""
    while True:
        try:
            r.ping()
            print("Conectado ao Redis.")
            return
        except redis.exceptions.ConnectionError as exc:
            print(f"Redis indisponível, tentando novamente em 5s: {exc}")
            time.sleep(5)


def criar_conexao_rabbitmq() -> pika.BlockingConnection:
    """Cria e retorna uma conexão bloqueante com o RabbitMQ."""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=60,
                    blocked_connection_timeout=300,
                )
            )
            print("Conectado ao RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as exc:
            print(f"RabbitMQ indisponível, tentando novamente em 5s: {exc}")
            time.sleep(5)


def escutar_rabbitmq_e_alimentar_redis() -> None:
    """Roda em background para mover itens da fila do RabbitMQ para o pool no Redis."""
    aguardar_redis()

    while True:
        connection = criar_conexao_rabbitmq()
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        def callback(ch, method, properties, body):
            desafio = json.loads(body)
            r.lpush(REDIS_POOL_KEY, json.dumps(desafio))
            r.ltrim(REDIS_POOL_KEY, 0, REDIS_MAX_ITEMS - 1)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Consumido do RabbitMQ e guardado no Redis: {desafio.get('id')}")

        try:
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=False)
            channel.start_consuming()
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as exc:
            print(f"Conexão com RabbitMQ perdida. Reconectando: {exc}")
            time.sleep(5)
        finally:
            try:
                connection.close()
            except Exception:
                pass


@app.on_event("startup")
def startup_event() -> None:
    thread = threading.Thread(target=escutar_rabbitmq_e_alimentar_redis, daemon=True)
    thread.start()


@app.get("/health")
def healthcheck() -> dict:
    """Endpoint de verificação de integridade (Healthcheck) da aplicação."""
    redis_ok = True
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        redis_ok = False

    return {
        "status": "ok",
        "redis": redis_ok,
        "rabbitmq_host": RABBITMQ_HOST,
        "redis_pool_key": REDIS_POOL_KEY,
    }


@app.get("/desafio")
def obter_desafio() -> dict:
    """Retorna um desafio do pool do Redis ou do fallback estático."""
    try:
        desafio_json = r.rpop(REDIS_POOL_KEY)
        if desafio_json:
            return {"origem": "Pool_Redis (Gerado via RabbitMQ)", "desafio": json.loads(desafio_json)}
        return {"origem": "Fallback_Estatico (Pool Vazio)", "desafio": random.choice(BANCO_ESTATICO_FALLBACK)}
    except redis.exceptions.ConnectionError:
        return {
            "origem": "Fallback_Estatico (Sistema de Cache Fora do Ar)",
            "desafio": random.choice(BANCO_ESTATICO_FALLBACK),
        }
