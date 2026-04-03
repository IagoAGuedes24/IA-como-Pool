# POC 4: IA como Pool-Não Dependência Síncrona

**Disciplina:** Engenharia de Sistemas Distribuídos (2025.2)  
**Equipe:** Brendo de Almeida Mendonça, Emmanuel Gomes, Iago Albuquerque, Pedro Henrique Chagas, Sergio Andress Braz  

---

## Visão Geral do Projeto

Este projeto implementa uma arquitetura distribuída focada em alta disponibilidade e baixa latência, resolvendo o problema da dependência síncrona de Inteligências Artificiais. 

A POC simula um sistema de retenção de usuários em jogos mobile (onde o jogador responde a perguntas sobre um anúncio recém-assistido). Em vez de o usuário aguardar a IA gerar a pergunta em tempo real (o que causaria lentidão e risco de falha), um **Worker assíncrono (Generator)** utiliza a API da Groq (Llama 3.1) para pré-gerar as perguntas e armazená-las em um **Pool de Cache (Redis)** via **Mensageria (RabbitMQ)**. A API Principal (Consumer) apenas consome este pool em milissegundos.

### Padrões Arquiteturais Aplicados
* **Event-Driven Architecture / Queues:** Desacoplamento via RabbitMQ.
* **Cache-Aside Pattern:** Leitura ultrarrápida utilizando Redis como Pool.
* **Fallback / Graceful Degradation:** Banco estático de perguntas de retenção caso a IA e o Pool falhem.
* **Circuit Breaker / Isolation:** Serviços rodando em contêineres Docker isolados.

---

## Tecnologias Utilizadas
* **Backend:** Python 3.9, FastAPI, Uvicorn
* **Mensageria & Cache:** RabbitMQ, Redis
* **IA:** Groq API (Modelo: `llama-3.1-8b-instant`)
* **Infraestrutura:** Docker & Docker Compose

---

## Como Executar o Projeto

### Pré-requisitos
* Ter o [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando.
* Ter uma conta e uma chave de API gratuita na [Groq Console](https://console.groq.com/).
* Ter o Git instalado.

### Passo a Passo

1. **Clone este repositório:**
   <pre>
   git clone https://github.com/IagoAGuedes24/IA-como-Pool
   cd IA-como-Pool </pre>

2. **Configure as Variáveis de Ambiente:**

* Navegue até a pasta docker/
* Crie um arquivo chamado .env baseado no arquivo .env.examplo
* Insira a sua chave da Groq no arquivo .env:
<pre> GROQ_API_KEY=gsk_suachaveaqui... </pre>

3. **Suba a Infraestrutura com Docker:**
* Dentro da pasta docker/, execute o comando:
<pre> docker-compose up --build -d </pre>

**OBS: O RabbitMQ leva cerca de 15 a 20 segundos para inicializar completamente antes que o Generator comece a popular o Pool**

4. **Acesso e testes**
* Acesse o consumo do Pool: http://localhost:8000/desafio
* Atualize a página múltiplas vezes
***Resultado esperado:*** Respostas instantâneas com a origem indicando Pool_Redis Gerado via RabbitMQ. O usuário não sofre com o tempo de processamento da IA
***Observação de Pool:*** Para visualizar a geração das perguntas basta dar o comando:
  <pre> docker-compose logs -f generator </pre>

* No terminal, derrube propositalmente o serviço gerador
<pre> docker-compose stop generator </pre>
* Volte ao navegador e continue atualizando a página

***Resultado Esperado:*** O sistema continuará servindo os itens restantes no cache. Assim que o Pool do Redis esvaziar, o sistema não apresentará erro. Ele fará a transição automática para as respostas estáticas de contingência, indicando a origem "Fallback_Estatico com Pool vazio
