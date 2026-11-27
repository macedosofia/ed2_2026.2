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

**Entrega:** 24/11/2026.

A Árvore B funciona como índice dos clientes, utilizando o ID único como chave e associando cada chave à posição do registro em um array mantido em memória pelo `ClientService`.

Os registros completos são armazenados separadamente da árvore. A busca por ID percorre a Árvore B, recupera a posição correspondente e permite acessar diretamente o registro no array.

A aplicação permite cadastrar, listar e editar clientes, associar eSIMs e pacotes e gravar as alterações em JSON.

### Organização dos dados

- Árvore B: armazena IDs e posições dos registros.
- Array de clientes: armazena os registros completos.
- JSON: mantém os registros de forma persistente.
- ClientService: coordena as operações e mantém a consistência entre a árvore e o array.

Durante a inicialização, os registros são carregados do JSON para o array e seus IDs são indexados na Árvore B.

Novos clientes são acrescentados ao final do array, preservando as posições existentes. A listagem utiliza o percurso em ordem da árvore, sem reorganizar o array.

As atualizações preservam o ID e a posição do cliente, modificando apenas o registro correspondente.

Em caso de falha durante uma mutação, o serviço restaura o estado anterior da árvore, do array e das métricas.

A consulta cliente × destino combina a Árvore B, a Tabela Hash e o catálogo de pacotes. A instrumentação mostra o tamanho, a altura, o número de nós, as divisões e as buscas da árvore.

A aplicação também disponibiliza:

- Carregamento de clientes a partir de arquivos JSON.
- Base demonstrativa de 1.000 clientes gerados automaticamente.
- Busca por ID utilizando a Árvore B como índice.
- Listagem ordenada pelo percurso da árvore.
- Instrumentação da carga e das consultas.
- Planejador Multidestinos integrado à aplicação Flask.
- Testes automatizados de estruturas, serviços, persistência e rotas.

A base demonstrativa está disponível em [`globalsim/data/clients.demo.json`](globalsim/data/clients.demo.json).

O gerador determinístico está em [`scripts/generate_clients_demo.py`](scripts/generate_clients_demo.py), e seu funcionamento é explicado na [documentação da base demonstrativa](docs/client_seed.md).

Para utilizar os 1.000 clientes no Flask sem modificar os dados principais da aplicação, siga a [preparação do roteiro de demonstração](docs/stage2_delivery.md#preparação).

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

Na revisão `7951f69` da branch `dev`, a suíte completa foi executada com **225 testes aprovados**, incluindo os testes de integração do Planejador e os testes da base demonstrativa de clientes.

Após a correção da Árvore B para funcionar como índice de posições, em 27/11/2026, a suíte completa foi executada com **240 testes aprovados**, sem falhas ou erros, utilizando Python 3.10.12.

Os testes adicionais verificam a consistência entre a Árvore B e o array, a preservação das posições, o acesso direto aos registros, a reconstrução do índice e o rollback, inclusive após divisões de nós.

O [guia da Etapa 2](docs/stage2_delivery.md#execução-e-testes) apresenta a arquitetura, o checklist de requisitos e o roteiro de demonstração.

## Diferencial da equipe

O **Planejador Multidestinos com Recomendação Automática de Pacotes eSIM** está disponível na aplicação principal.

Ele consulta a cobertura dos destinos e recomenda um pacote que atenda ao roteiro, à duração e ao consumo estimado.

A seleção prioriza:

1. Menor franquia de dados suficiente.
2. Menor validade excedente.
3. Menor código identificador, em caso de empate.

Com um ID de cliente, a tela mostra o eSIM e o pacote atual para comparação com a recomendação.

O Planejador reutiliza os serviços de países, clientes e pacotes existentes na aplicação, integrando consultas à Tabela Hash e à Árvore B.

A proposta foi aprovada pela professora.

## Etapa 3 — Grafo

A próxima etapa acrescentará a rede internacional ponderada por latência, a visualização do Grafo, BFS, DFS, Dijkstra e a integração de rotas de menor latência à consulta de conectividade.

## Documentação

- [Etapa 2 — checklist do enunciado, arquitetura e roteiro de demonstração](docs/stage2_delivery.md)
- [Base demonstrativa de 1.000 clientes](docs/client_seed.md)
- [Gerenciamento Web de clientes](docs/client_web.md)
- [Contratos dos serviços](docs/contracts.md)
- [Descrição do diferencial](docs/differential.md)
- [Documentação histórica da Etapa 1](globalsim/README.md)
- [Checklist e roteiro da primeira entrega](docs/delivery_1.md)