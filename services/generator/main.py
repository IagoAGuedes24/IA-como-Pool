import pika
import time
import json
import os
from openai import OpenAI

#aguarda o RabbitMQ iniciar completamente
time.sleep(15)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='fila_ia_desafios')

#inicializa o cliente apontando para a Groq!
CHAVE_API = os.environ.get("GROQ_API_KEY")
client = OpenAI(
    api_key=CHAVE_API,
    base_url="https://api.groq.com/openai/v1" #puxa a API groq
)

def gerar_desafio_ia_gratuita():
    if not CHAVE_API:
        print("ERRO: Chave da Groq não encontrada!")
        time.sleep(10)
        return None
    #passando instruções para geração de desafios
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": "Você é uma IA de retenção de usuários em um jogo móvel. O jogador acabou de assistir a um vídeo publicitário (ad) para ganhar uma recompensa. Retorne APENAS um JSON válido contendo: 'id' (inteiro aleatório de 4 dígitos), 'pergunta' (texto curto testando a atenção do usuário ao vídeo) e 'resposta' (solução direta)."
                },
                {
                    "role": "user", 
                    "content": "Gere um desafio de retenção sobre um vídeo comercial fictício da 'Red Bull' onde um atleta salta de paraquedas de um balão."
                }
            ],
            response_format={ "type": "json_object" },
            max_tokens=150,
            temperature=0.7
        )
        
        conteudo = response.choices[0].message.content
        return json.loads(conteudo)
    except Exception as e:
        print(f"Erro ao comunicar com a IA: {e}")
        return None

print("Iniciando Generator com Llama 3 (Groq)...")

while True:
    novo_desafio = gerar_desafio_ia_gratuita()
    
    if novo_desafio:
        channel.basic_publish(
            exchange='',
            routing_key='fila_ia_desafios',
            body=json.dumps(novo_desafio)
        )
        print(f"Desafio gerado pela IA (Groq) e enviado: ID {novo_desafio.get('id')}")
    
    time.sleep(5)