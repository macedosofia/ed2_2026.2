# Contratos implementados — entrega 1

Contratos da implementação inicial, atualizados após a refatoração da Tabela Hash para o `dict` do Python. Os nomes abaixo refletem a organização em inglês; as mensagens e os campos do enunciado permanecem em português.

## Checklist de implementação — revisado em 23/10/2026

- [x] Modelo com campos obrigatórios, normalização e código imutável na edição.
- [x] Tabela Hash baseada em `dict`, com inserção, busca, atualização, remoção e listagem.
- [x] Instrumentação das operações da estrutura.
- [x] Carga JSON na Hash durante a inicialização.
- [x] Consultas e mutações pelo serviço, usando a Hash.
- [x] Persistência após mutações e restauração do estado anterior em caso de falha.
- [x] Preservação do arquivo JSON inválido.
- [x] Rotas e templates integrados, com mutações por POST e redirecionamento 303.
- [x] Testes de integração com aplicação e arquivos temporários isolados.
- [x] Revisão técnica dos contratos contra o código e os testes da Etapa 1.

## Etapa 1 — definir os dados

Adotar registros com `codigo`, `pais`, `regiao`, `operadora` e `tecnologia`. Normalizar o código com remoção de espaços externos e letras maiúsculas. Adotar duas letras ASCII como convenção. O código permanece imutável na edição. O modelo valida campos; o serviço verifica unicidade pela Hash.

## Etapa 2 — fechar a interface da Hash

| Operação implementada | Resultado |
|---|---|
| insert(record) | Inserir cópia do registro; sinalizar código duplicado |
| find(code) | Retornar cópia do registro ou ausência |
| update(code, record) | Alterar campos sem mudar a chave; sinalizar ausência |
| remove(code) | Retornar registro removido; sinalizar ausência |
| list_all() | Retornar cópias de todos os registros armazenados |
| statistics() | Retornar quantidade de registros, chaves e métricas das operações |

`insert` e `update` retornam `None` em caso de sucesso; `find` retorna um registro ou `None`; `remove` retorna o registro removido; `list_all` retorna uma lista; `statistics` retorna um dicionário de métricas. Duplicidade e troca de chave geram `ValueError`; atualização e remoção de chave ausente geram `LookupError`. A implementação utiliza o dicionário nativo (`dict`) do Python para armazenar os registros, utilizando os códigos dos países como chaves.

A instrumentação registra a quantidade de países cadastrados (`size`), as chaves existentes (`keys`), os registros carregados inicialmente (`loaded_records`), as buscas realizadas (`lookups`), as buscas bem-sucedidas (`hits`), as buscas sem resultado (`misses`), as inserções (`insertions`), as atualizações (`updates`) e as remoções (`removals`). Como o `dict` gerencia internamente seus baldes e colisões, essas informações não são contabilizadas diretamente pela aplicação.

## Etapa 3 — integrar persistência e serviço

1. Inicialização: JSON → validação dos registros → inserção na Hash → registro das rotas.
2. Consulta/listagem: rota → serviço → Hash → template.
3. Mutação: formulário POST → validação → Hash → listagem da Hash → gravação JSON → redirecionamento GET.
4. Falha de gravação: restaurar a cópia anterior da Hash, incluindo registros e métricas, e sinalizar erro.
5. JSON inválido: preservar arquivo e informar erro; não converter corrupção em base vazia.
6. Testes: fornecer caminho temporário e nova instância da aplicação/Hash para cada cenário.

O módulo de persistência só lê e grava. A Hash não conhece Flask, templates nem arquivos. O serviço coordena regras e persistência. As rotas cuidam de HTTP.

## Etapa 4 — alinhar rotas e templates

| Método | Caminho implementado | Finalidade | Template |
|---|---|---|---|
| GET | `/` | Página inicial | index.html |
| GET | `/countries` | Listar países | countries.html |
| GET / POST | `/countries/new` | Exibir formulário / cadastrar | country_form.html |
| GET | `/coverage` | Consultar código via parâmetro `codigo` | coverage.html |
| GET / POST | `/countries/<code>/edit` | Exibir formulário / atualizar | country_form.html |
| POST | `/countries/<code>/delete` | Remover e redirecionar | — |
| GET | `/instrumentation` | Observar a Hash | instrumentation.html |

Usar os nomes de campos do registro nos formulários. Após mutação bem-sucedida, aplicar Post/Redirect/Get. Em erro de validação, preservar campos e exibir a causa; códigos inexistentes e falhas de arquivo não devem parecer operações bem-sucedidas. GET nunca altera registros.


## Serviço de clientes (ClientService)

O serviço de clientes está localizado em
`globalsim/services/clients.py` e utiliza a Árvore B
como estrutura principal de armazenamento em memória.

### Estrutura do cliente

| Campo | Tipo | Regra |
|---|---|---|
| id | int | Inteiro positivo, único e imutável |
| nome | str | Texto não vazio |
| email | str | Endereço de e-mail válido |
| esim | str ou None | Identificador do eSIM |
| pacote | int ou None | Identificador positivo do pacote |
| status | str | Texto não vazio |

Os campos `esim` e `pacote` podem receber `None`
quando ainda não existe uma associação.

### Interface pública

| Método | Retorno | Responsabilidade |
|---|---|---|
| ClientService(path) | Instância | Carrega os clientes do JSON |
| create(record) | None | Cadastra um cliente |
| find(client_id) | dict ou None | Busca um cliente pelo ID |
| list_all() | list | Lista os clientes em ordem crescente de ID |
| update(client_id, changes) | None | Atualiza parcialmente um cliente |
| statistics() | dict | Retorna as métricas da Árvore B |

### Regras de atualização

- O ID do cliente não pode ser alterado.
- Os campos não informados permanecem inalterados.
- Campos desconhecidos são rejeitados.
- Os dados atualizados passam pela validação do modelo.
- A associação de eSIM e pacote utiliza o método update().

### Exceções

- ValueError: ID inválido, ID duplicado, dados inválidos,
  campo desconhecido ou tentativa de alterar o ID.
- LookupError: tentativa de atualizar cliente inexistente.
- OSError: falha de acesso ou gravação do arquivo.

### Persistência e integridade

A persistência está localizada em
`globalsim/persistence/clients_json.py`.

- O JSON é carregado durante a inicialização do serviço.
- A Árvore B é utilizada nas operações em memória.
- O JSON é atualizado após cada cadastro ou atualização.
- A gravação utiliza arquivo temporário e substituição atômica.
- Em caso de falha, o serviço restaura os registros e
  as estatísticas anteriores da Árvore B.
- As operações são protegidas por RLock.
- Os registros retornados são cópias dos dados armazenados.
- Arquivos inválidos não são sobrescritos automaticamente.

### Estatísticas da Árvore B

| Métrica | Descrição |
|---|---|
| size | Quantidade de clientes |
| height | Altura da árvore |
| node_count | Quantidade de nós |
| splits | Quantidade de divisões de nós |
| lookups | Quantidade de buscas realizadas |

### Limitações e integração

- A disponibilidade do eSIM será validada na integração.
- A existência do pacote no catálogo será validada na integração.
- A integração com Flask e os demais módulos será realizada
  nas respectivas etapas do projeto.
- A exclusão de clientes não está implementada.
- O rollback utiliza uma cópia da árvore, com custo adicional
  de tempo e memória proporcional ao tamanho da estrutura.

### Testes automatizados

- tests/test_client.py: 11 testes.
- tests/test_clients_json.py: 9 testes.
- tests/test_client_service.py: 24 testes.

Total de 44 testes relacionados ao gerenciamento de clientes,
incluindo carregamento de 1.000 registros, persistência,
validação, atualização e rollback.
