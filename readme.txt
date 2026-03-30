# IA como Pool (Não Dependência Síncrona)

## Visão Geral

Este projeto tem como objetivo demonstrar uma arquitetura de sistemas distribuídos onde serviços de Inteligência Artificial (IA) são desacoplados do fluxo crítico da aplicação.

A proposta central é evitar dependência síncrona de IA, utilizando um modelo baseado em pool assíncrono de dados previamente gerados, garantindo maior resiliência, escalabilidade e desempenho.

---

## Problema

Sistemas que dependem diretamente de chamadas síncronas para serviços de IA enfrentam:

* Alta latência
* Baixa disponibilidade quando a IA falha
* Custo elevado por requisição em tempo real

Este projeto busca resolver esses problemas através de uma arquitetura desacoplada.

---

## Solução Proposta

A solução consiste em um sistema distribuído onde:

1. Um serviço gera conteúdos de forma assíncrona utilizando IA ou mocks
2. Esses conteúdos são armazenados em um pool
3. O sistema principal consome desse pool em tempo real
4. Caso o pool esteja vazio, um fallback é utilizado

---

## Arquitetura (Visão Inicial)

### Serviços principais:

* Generator Service: gera conteúdo via IA 
* Queue (Broker): gerencia comunicação assíncrona
* Pool Storage: armazena conteúdos prontos
* Consumer Service: consome conteúdo em tempo real
* Fallback Service: fornece conteúdo alternativo

---

## Padrões Arquiteturais Utilizados

* Event-Driven Architecture
* Queue / PubSub
* Cache-Aside Pattern
* Circuit Breaker
* Bulkhead / Isolation

---

## Plano Inicial de Testes

* Teste de consumo do pool
* Teste de fallback quando o pool está vazio
* Simulação de indisponibilidade da IA
* Teste de carga básica (requisições simultâneas)

---

## Critérios de Sucesso

* O sistema deve continuar funcionando mesmo com a IA indisponível
* O tempo de resposta deve permanecer baixo com uso do pool
* O fallback deve ser acionado corretamente
* A arquitetura deve demonstrar desacoplamento efetivo

---

## Equipe

Pedro Henrique Chagas
Iago Albuquerque
Brendo de Almeida
Emmanuel Gomes Mendonça
Sergio Andress Braz

---

## Status do Projeto

Em fase inicial (definição de arquitetura e setup do ambiente)

---

## Videocast

Será adicionado posteriormente