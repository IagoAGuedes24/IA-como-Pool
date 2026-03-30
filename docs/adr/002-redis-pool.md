# ADR 002 — Uso de Redis como Pool

## Status
Aceito

## Contexto
É necessário armazenar conteúdos pré-gerados com acesso rápido.

## Decisão
Utilizar Redis como armazenamento do pool de conteúdos.

## Consequências
Positivas:
- Baixa latência
- Alta performance

Negativas:
- Dados voláteis