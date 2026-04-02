import json
import os
import time
import logging
import pika
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE", "fila_ia_desafios")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
PUBLISH_INTERVAL_SECONDS = int(os.environ.get("PUBLISH_INTERVAL_SECONDS", "5"))

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


def criar_conexao_rabbitmq() -> pika.BlockingConnection:
    logging.info("Tentando conectar ao RabbitMQ...")
    """Tenta conectar ao RabbitMQ indefinidamente até o broker ficar disponível."""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=60,
                    blocked_connection_timeout=300,
                )
            )
            logging.info("Conectado ao RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as exc:
            logging.warning(f"RabbitMQ indisponível, tentando novamente em 5s: {exc}")
            time.sleep(5)


def criar_canal(connection: pika.BlockingConnection) -> pika.adapters.blocking_connection.BlockingChannel:
    """cria e declara o canal no RabbitMQ."""
    logging.info(f"Criando canal e declarando fila '{RABBITMQ_QUEUE}'")
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return channel


def gerar_desafio_ia() -> dict | None:
    """gera um desafio utilizando a IA."""
    if not GROQ_API_KEY:
        logging.warning("GROQ_API_KEY não configurada. Aguardando...")
        time.sleep(10)
        return None

    try:
        logging.info("Gerando novo desafio com IA...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma IA de retenção de usuários em um jogo móvel. "
                        "O jogador acabou de assistir a um vídeo publicitário para ganhar uma recompensa. "
                        "Retorne APENAS um JSON válido contendo: 'id' (inteiro aleatório de 4 dígitos), "
                        "'pergunta' (texto curto testando a atenção do usuário ao vídeo) e 'resposta' "
                        "(solução direta)."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Gere um desafio de retenção sobre um vídeo comercial fictício da 'Red Bull' "
                        "onde um atleta salta de paraquedas de um balão."
                    ),
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=150,
            temperature=0.7,
        )
        conteudo = response.choices[0].message.content
        return json.loads(conteudo)
    except Exception as exc:
        logging.error(f"Erro ao comunicar com a IA: {exc}")
        return None


def publicar_desafio(channel: pika.adapters.blocking_connection.BlockingChannel, desafio: dict) -> None:
    """publica um desafio na fila do RabbitMQ."""
    logging.debug(f"Publicando desafio ID {desafio.get('id')} na fila...")
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(desafio),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    logging.info(f"Desafio publicado na fila (ID: {desafio.get('id')})")


logging.info("Iniciando Generator com Llama 3 (Groq)...")

while True:
    connection = criar_conexao_rabbitmq()
    channel = criar_canal(connection)

    try:
        while True:
            novo_desafio = gerar_desafio_ia()
            if novo_desafio:
                publicar_desafio(channel, novo_desafio)
                logging.info(f"Desafio gerado e enviado para a fila: ID {novo_desafio.get('id')}")
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as exc:
        logging.error(f"Conexão com RabbitMQ perdida. Reconectando: {exc}")
        time.sleep(5)
    finally:
        logging.info("Encerrando conexão com RabbitMQ...")
        try:
            connection.close()
        except Exception:
            logging.warning("Erro ao fechar conexão (ignorando).")
            pass
