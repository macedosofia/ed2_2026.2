# GlobalSIM — Estruturas de Dados II

Projeto acadêmico de Estruturas de Dados II do curso de Sistemas de Informação da Universidade do Estado da Bahia (UNEB).

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
| 3 | Grafo | Rede internacional e conectividade (previsto) |

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

## Etapa 2 — Árvore B

**Entrega em 24/11/2026.** A Árvore B armazena e busca clientes pelo ID único. A aplicação permite cadastrar, listar e editar clientes, associar eSIMs e pacotes e gravar as alterações em JSON. A consulta cliente × destino combina a Árvore B, a Tabela Hash e o catálogo de pacotes. A instrumentação mostra o tamanho, a altura, o número de nós, as divisões e as buscas da árvore.

A carga de clientes por JSON já funciona. A base demonstrativa de 1.000 clientes aguarda a integração do [PR #19](https://github.com/macedosofia/ed2_2026.2/pull/19). Após o merge, siga a [preparação do roteiro](docs/stage2_delivery.md#preparação) para abrir uma cópia da base no Flask.

## Como executar

Requer Python 3.10 ou superior.

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app globalsim.app:create_app run --debug
```

Abra [http://127.0.0.1:5000](http://127.0.0.1:5000). Use o menu ou acesse os caminhos abaixo pelo navegador.

| Recurso | Caminho |
|---|---|
| Países e consulta de cobertura | `/countries` e `/coverage` |
| Instrumentação da Tabela Hash | `/instrumentation` |
| Clientes, busca e edição | `/clients` |
| Consulta cliente × país | `/clients/coverage` |
| Instrumentação da Árvore B | `/clients/instrumentation` |
| Planejador Multidestinos | `/trip-planner` |

## Como executar os testes

Com o ambiente virtual ativado, na raiz do repositório:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -q
```

O [guia da Etapa 2](docs/stage2_delivery.md#execução-e-testes) registra o resultado da suíte e a revisão verificada.

## Diferencial da equipe

O **Planejador Multidestinos com Recomendação Automática de Pacotes eSIM** está disponível na aplicação principal. Ele consulta a cobertura dos destinos e recomenda um pacote que atenda ao roteiro, à duração e ao consumo estimado. A seleção prioriza menor franquia suficiente, menor validade excedente e menor código. Com um ID de cliente, a tela mostra o pacote atual para comparação. A proposta foi aprovada pela professora.

## Etapa 3 — Grafo

A próxima etapa acrescentará a rede internacional ponderada por latência, a visualização do Grafo, BFS, DFS, Dijkstra e a integração de rotas de menor latência à consulta de conectividade.

## Documentação

- [Etapa 2 — checklist do enunciado, arquitetura e roteiro de demonstração](docs/stage2_delivery.md)
- [Gerenciamento Web de clientes](docs/client_web.md)
- [Descrição do diferencial](docs/differential.md)
- [Documentação histórica da Etapa 1](globalsim/README.md)
- [Checklist e roteiro da primeira entrega](docs/delivery_1.md)
