# GlobalSIM — Estruturas de Dados II

Projeto acadêmico desenvolvido para a disciplina de Estruturas de Dados II.

**Repositório:** ed2_2026.2

## Equipe

- Anderson de Jesus Soledade Filho
- João Cleber Freire Ramos Pinto
- Sofia Macêdo Costa

## Sobre o projeto

O GlobalSIM é uma aplicação Web desenvolvida em Python e Flask para simular a administração de serviços internacionais de Internet móvel por eSIM.

O desenvolvimento está dividido em três etapas:

| Etapa | Estrutura | Funcionalidade principal |
|---|---|---|
| 1 | Tabela Hash | Países atendidos e cobertura |
| 2 | Árvore B | Clientes e eSIMs |
| 3 | Grafo | Rede internacional e conectividade |

## Etapa 1 — Tabela Hash

**Entrega:** 20/10/2026

A Etapa 1 implementa:

- Página inicial.
- Cadastro de países.
- Consulta de cobertura.
- Listagem de países.
- Edição e remoção.
- Tabela Hash com encadeamento separado.
- Persistência em JSON.
- Instrumentação da estrutura.
- Validações e tratamento de erros.
- Testes automatizados.

A implementação oficial da Etapa 1 está na pasta
[`preparations/`](preparations/).

## Como executar

Requer Python 3.10 ou superior.

Na raiz do repositório:

```bash
cd preparations
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Abra:

http://127.0.0.1:5000

## Como executar os testes

Dentro de `preparations`:

```bash
python -m unittest discover -s tests -v
```

## Diferencial da equipe

**Planejador Multidestinos com Recomendação Automática
de Pacotes eSIM.**

A funcionalidade permitirá analisar múltiplos destinos internacionais, verificar cobertura e recomendar um pacote adequado à duração e ao consumo estimado da viagem.

Nas etapas seguintes, o planejamento será integrado à
Árvore B e ao Grafo.

**Status:** Proposta submetida à professora, aguardando aprovação.

## Documentação

- [Documentação da Etapa 1](preparations/README.md)
- [Descrição do diferencial](preparations/docs/differential.md)

O projeto será desenvolvido incrementalmente, preservando as funcionalidades das etapas anteriores.