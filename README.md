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
- Tabela Hash utilizando o dicionário nativo (`dict`) do Python.
- Persistência em JSON.
- Instrumentação da estrutura.
- Validações e tratamento de erros.
- Testes automatizados.

A implementação oficial da Etapa 1 está na pasta [`globalsim/`](globalsim/).

A Tabela Hash utiliza o `dict` do Python para armazenar os países, utilizando seus códigos internacionais como chaves. A classe `HashTable` encapsula as operações de inserção, busca, atualização e remoção, com complexidade média esperada O(1).

A instrumentação permite acompanhar a quantidade de países, buscas realizadas, buscas bem-sucedidas, buscas sem resultado, inserções, atualizações e remoções.

A base inicial já contém os oito países de demonstração. A versão final da entrega original é identificada pela tag `etapa-1-final`; a tag `etapa-1` preserva o marco anterior da equipe.

## Como executar

Requer Python 3.10 ou superior.

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app globalsim.app:create_app run --debug
```

Abra:

http://127.0.0.1:5000

## Como executar os testes

Com o ambiente virtual ativado, na raiz do repositório:

```bash
python -m unittest discover -s tests -v
```

Validação em 20/10/2026: **25 testes aprovados**, incluindo validação dos registros, falhas de persistência e os oito países de demonstração.

Após a refatoração da Tabela Hash para `dict`, em 23/10/2026, foram executados **30 testes com sucesso**, incluindo operações da estrutura, instrumentação, persistência JSON e rotas Flask.

## Diferencial da equipe

**Planejador Multidestinos com Recomendação Automática de Pacotes eSIM.**

A funcionalidade permitirá analisar múltiplos destinos internacionais, verificar cobertura e recomendar um pacote adequado à duração e ao consumo estimado da viagem.

A recomendação utilizará critérios determinísticos para selecionar um único pacote que atenda aos destinos, à quantidade de dados e à validade necessária.

Nas etapas seguintes, o planejamento será integrado à Árvore B e ao Grafo.

**Status:** Proposta aprovada pela professora.

## Documentação

- [Documentação da Etapa 1](globalsim/README.md)
- [Descrição do diferencial](docs/differential.md)
- [Checklist e roteiro da primeira entrega](docs/delivery_1.md)

O projeto será desenvolvido incrementalmente, preservando as funcionalidades das etapas anteriores.