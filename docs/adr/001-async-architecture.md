# ADR 001 — Uso de Arquitetura Assíncrona

## Status
Aceito

## Contexto
O sistema depende de geração de conteúdo por IA, que pode apresentar latência e indisponibilidade.

## Decisão
Adotar comunicação assíncrona entre serviços utilizando fila (RabbitMQ).

## Consequências
Positivas:
- Maior resiliência
- Desacoplamento entre serviços

Negativas:
- Maior complexidade arquitetural 