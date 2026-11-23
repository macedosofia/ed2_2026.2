# Gerenciamento Web de Clientes — GlobalSIM

## 1. Objetivo

A feature `feature/client-web` disponibiliza uma interface web para gerenciamento de clientes, utilizando a Árvore B como estrutura de armazenamento e busca por identificadores.

A implementação integra os serviços de clientes, países e pacotes à aplicação Flask, preservando as funcionalidades existentes da Etapa 1.

## 2. Funcionalidades implementadas

- Listagem de clientes em ordem crescente de ID.

- Busca de clientes por ID.

- Visualização dos detalhes de um cliente.

- Cadastro de novos clientes.

- Edição de clientes existentes.

- Associação de eSIM e pacote de dados.

- Persistência dos registros em JSON.

- Consulta integrada de cobertura entre clientes e países.

- Instrumentação da Árvore B.

## 3. Estruturas de dados

### Árvore B

A Árvore B armazena os clientes utilizando o ID como chave única.

As inserções, buscas e atualizações são realizadas pelo `ClientService`, utilizando a estrutura de dados mantida em memória.

### Tabela Hash

A Tabela Hash é utilizada para consultar países por seus respectivos códigos.

A consulta integrada utiliza a Árvore B para localizar o cliente e a Tabela Hash para localizar o país.

### Catálogo de pacotes

O `PackageService` disponibiliza os pacotes registrados no catálogo e permite verificar se determinado país está incluído no pacote associado ao cliente.

## 4. Rotas disponibilizadas

| Método | Rota | Funcionalidade |
|---|---|---|
| GET | `/clients` | Listagem de clientes |
| GET | `/clients/search?id=58372` | Busca por ID |
| GET | `/clients/58372` | Detalhes do cliente |
| GET | `/clients/new` | Formulário de cadastro |
| POST | `/clients/new` | Cadastro de cliente |
| GET | `/clients/58372/edit` | Formulário de edição |
| POST | `/clients/58372/edit` | Atualização do cliente |
| GET | `/clients/coverage` | Consulta integrada de cobertura |
| GET | `/clients/instrumentation` | Estatísticas da Árvore B |

## 5. Validação dos registros

O cadastro e a edição realizam as seguintes validações:

- ID inteiro positivo e único.

- Nome obrigatório.

- E-mail válido.

- Status obrigatório.

- eSIM opcional.

- Pacote opcional, com código existente no catálogo quando informado.

- Impossibilidade de alterar o ID de um cliente existente.

Em caso de sucesso no cadastro ou na edição, a aplicação redireciona o usuário para a página de detalhes.

## 6. Consulta integrada de cobertura

A consulta integrada permite informar o ID de um cliente e o código de um país.

Exemplo:

`/clients/coverage?client_id=58372&codigo=IT`

A aplicação apresenta os dados do cliente, as informações de cobertura do país e, quando disponível, os dados do pacote contratado.

A compatibilidade geográfica do pacote é verificada por meio da lista de países incluídos no catálogo.

A existência de cobertura cadastrada não implica necessariamente que o país esteja incluído no pacote do cliente. A compatibilidade geográfica também não representa uma autorização de uso baseada no status do cliente.

As consultas utilizam diretamente as estruturas de dados em memória, sem recarregar os arquivos JSON.

## 7. Instrumentação da Árvore B

A rota `/clients/instrumentation` apresenta as seguintes métricas:

| Métrica | Descrição |
|---|---|
| `size` | Quantidade de clientes cadastrados |
| `height` | Altura da árvore |
| `node_count` | Quantidade de nós |
| `splits` | Quantidade de divisões de nós |
| `lookups` | Quantidade de buscas realizadas |

As métricas são obtidas diretamente da Árvore B em memória.

O contador de buscas inclui consultas bem-sucedidas, consultas sem resultado e buscas internas realizadas durante atualizações.

Consultar a página de instrumentação não incrementa o contador de buscas.

Os contadores não são persistidos no JSON. Ao reiniciar a aplicação, a árvore é reconstruída a partir dos registros armazenados, e as divisões decorrentes desse carregamento são contabilizadas.

## 8. Persistência

Os caminhos padrão dos arquivos de dados são:

- `globalsim/data/clients.json`

- `globalsim/data/countries.json`

- `globalsim/data/packages.json`

A aplicação permite configurar caminhos alternativos por meio de:

- `CLIENTS_PATH`

- `COUNTRIES_PATH`

- `PACKAGES_PATH`

As operações de leitura não realizam alterações nos arquivos de dados.

Os testes automatizados utilizam arquivos temporários para preservar os dados originais do projeto.

## 9. Execução da aplicação

A partir da raiz do repositório, com o ambiente virtual ativo e as dependências instaladas, execute:

```bash

python -m flask --app globalsim.app run

```

Acesse:

`http://127.0.0.1:5000`

## 10. Testes automatizados

Para executar somente os testes das rotas de clientes:

```bash

python -m unittest discover -s tests -p "test_client_routes.py" -v

```

Para executar todos os testes do projeto:

```bash

python -m unittest discover -s tests -v

```

Para executar a versão resumida:

```bash

python -m unittest discover -s tests -q

```

### Resultados obtidos durante o desenvolvimento

| Indicador | Quantidade |
|---|---:|
| Testes existentes antes da feature | 108 |
| Novos testes adicionados | 61 |
| Testes das rotas de clientes | 61 |
| Total de testes aprovados | 169 |
| Falhas | 0 |

Os testes abrangem cadastro, edição, busca, listagem, persistência, validação de entradas, associação de pacotes, cobertura integrada e instrumentação da Árvore B.

Também verificam a preservação dos arquivos JSON, o uso direto das estruturas de dados e o tratamento de falhas de persistência.

## 11. Arquivos da implementação

- `globalsim/app.py`

- `globalsim/routes/clients.py`

- `globalsim/templates/base.html`

- `globalsim/templates/clients.html`

- `globalsim/templates/client_form.html`

- `globalsim/templates/client_detail.html`

- `globalsim/templates/client_coverage.html`

- `globalsim/templates/client_instrumentation.html`

- `tests/test_client_routes.py`

- `docs/client_web.md`

## 12. Histórico de implementação

A implementação foi organizada em commits incrementais:

1\. `9da91d8` — feat: register client services in Flask

2\. `3bd2773` — feat: add client listing and lookup routes

3\. `dae2639` — feat: add client forms and update routes

4\. `bab6bbc` — feat: integrate client and country coverage

5\. `90af505` — feat: add B-tree instrumentation page

## 13. Escopo

Esta feature é responsável pela interface web de gerenciamento de clientes e pela integração com as estruturas de dados e serviços existentes.

Funcionalidades relacionadas a grafos, algoritmos de caminhos e planejamento de viagens não fazem parte desta implementação.
