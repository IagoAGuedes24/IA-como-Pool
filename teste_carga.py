import requests
import time

url = "http://localhost:8000/desafio"
quantidade_requisicoes = 100
tempos = []

print(f"Iniciando teste de carga com {quantidade_requisicoes} requisições no Pool...")

for i in range(quantidade_requisicoes):
    inicio = time.time()
    resposta = requests.get(url)
    fim = time.time()
    
    tempo_ms = (fim - inicio) * 1000
    tempos.append(tempo_ms)

media = sum(tempos) / len(tempos)
tempo_maximo = max(tempos)
tempo_minimo = min(tempos)

print("\n=== RESULTADOS DO TESTE DE DESEMPENHO ===")
print(f"Total de requisições: {quantidade_requisicoes}")
print(f"Tempo Médio: {media:.2f} ms")
print(f"Tempo Mais Rápido: {tempo_minimo:.2f} ms")
print(f"Tempo Mais Lento: {tempo_maximo:.2f} ms")
print("=========================================")