# Contratos implementados — GlobalSIM

Contratos da implementação das Etapas 1 e 2, atualizados após a refatoração da Tabela Hash para o `dict` do Python e a correção da Árvore B como índice de posições.

Os nomes abaixo refletem a organização em inglês; as mensagens e os campos do enunciado permanecem em português.

## Checklist de implementação da Etapa 1 — revisado em 23/10/2026

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

## Árvore B de clientes (BTree)

A Árvore B está localizada em `globalsim/structures/b_tree.py` e funciona como índice dos registros de clientes.

A estrutura associa cada ID à posição correspondente no array mantido pelo `ClientService`.

### Estrutura dos nós

| Atributo | Tipo | Responsabilidade |
|---|---|---|
| leaf | bool | Indica se o nó é uma folha |
| keys | list[int] | Armazena as chaves ordenadas |
| positions | list[int] | Armazena as posições associadas às chaves |
| children | list[BTreeNode] | Armazena as referências para os filhos |

Cada elemento de `keys` possui uma posição correspondente no mesmo índice interno de `positions`.

Os nós não armazenam os registros completos dos clientes.

### Interface pública

| Método | Retorno | Responsabilidade |
|---|---|---|
| BTree(min_degree=3) | Instância | Inicializa uma árvore vazia |
| insert(client_id, position) | None | Associa um ID à posição de um registro |
| find(client_id) | int ou None | Retorna a posição associada ao ID |
| list_all() | list[int] | Retorna as posições em ordem crescente das chaves |
| statistics() | dict | Retorna as métricas da árvore |

### Regras de indexação

- O grau mínimo deve ser um inteiro maior ou igual a 2.
- A chave deve ser um inteiro.
- As chaves não podem ser duplicadas.
- A posição deve ser um inteiro não negativo.
- A posição zero representa um índice válido.
- `None` representa uma chave não encontrada.
- Chaves e posições devem permanecer associadas durante inserções e divisões.
- O percurso em ordem organiza as posições de acordo com as respectivas chaves.
- A árvore não conhece o array externo, os registros completos ou os arquivos JSON.
- A validade das posições em relação ao array é responsabilidade do `ClientService`.

O modelo e o serviço de clientes garantem adicionalmente que os IDs sejam positivos e imutáveis.

### Propriedades estruturais

Considerando o grau mínimo `t`:

- Cada nó possui no máximo `2t - 1` chaves.
- Nós não raiz possuem pelo menos `t - 1` chaves.
- Um nó interno possui um filho a mais do que a quantidade de chaves.
- Todas as folhas permanecem no mesmo nível.
- As chaves dentro de cada nó permanecem ordenadas.
- As subárvores respeitam os intervalos definidos pelas chaves do nó pai.
- A divisão promove a chave mediana e sua posição correspondente.

O grau mínimo padrão é 3.

### Exceções

- ValueError: grau mínimo inválido, ID de tipo inválido, posição inválida ou ID duplicado.
- ValueError: tentativa de dividir um filho que não está cheio ou promover uma mediana para um pai sem espaço.

### Complexidade

Para um grau mínimo fixo:

| Operação | Complexidade temporal |
|---|---|
| Busca por ID | O(log n) |
| Inserção de uma associação | O(log n) |
| Percurso completo em ordem | O(n) |
| Contagem de nós | O(n) |
| Cálculo da altura | O(log n) |

Esses custos correspondem às operações da estrutura de indexação, sem considerar persistência ou rollback do serviço.

## Serviço de clientes (ClientService)

O serviço de clientes está localizado em `globalsim/services/clients.py` e utiliza a Árvore B como índice dos registros armazenados em um array dinâmico em memória.

O serviço mantém duas estruturas:

- `self.tree`: Árvore B que associa IDs às posições.
- `self.clients`: lista Python que armazena os registros completos.

### Estrutura do cliente

| Campo | Tipo | Regra |
|---|---|---|
| id | int | Inteiro positivo, único e imutável |
| nome | str | Texto não vazio |
| email | str | Endereço de e-mail válido |
| esim | str ou None | Identificador do eSIM |
| pacote | int ou None | Identificador positivo do pacote |
| status | str | Texto não vazio |

Os campos `esim` e `pacote` podem receber `None` quando ainda não existe uma associação.

### Interface pública

| Método | Retorno | Responsabilidade |
|---|---|---|
| ClientService(path) | Instância | Carrega o array de clientes e constrói o índice a partir do JSON |
| create(record) | None | Cadastra e indexa um cliente |
| find(client_id) | dict ou None | Busca a posição na árvore e recupera o registro |
| list_all() | list | Lista os clientes em ordem crescente de ID |
| update(client_id, changes) | None | Atualiza parcialmente um cliente no array |
| statistics() | dict | Retorna as métricas da Árvore B |

### Regras de armazenamento e indexação

- Cada cliente ocupa uma posição no array.
- O ID de cada cliente possui uma associação na Árvore B.
- A quantidade de registros no array corresponde à quantidade de chaves indexadas.
- O cadastro utiliza `len(self.clients)` para determinar a próxima posição.
- Novos registros são acrescentados ao final do array.
- Registros existentes não são deslocados durante cadastros.
- A busca utiliza a Árvore B e realiza acesso direto ao array.
- A listagem utiliza o percurso em ordem da árvore.
- O array não é ordenado durante a listagem.
- As consultas não utilizam busca linear de clientes.
- O serviço é responsável por manter o índice consistente com o array.

### Regras de atualização

- O ID do cliente não pode ser alterado.
- A posição do cliente no array permanece a mesma.
- Os campos não informados permanecem inalterados.
- Campos desconhecidos são rejeitados.
- Os dados atualizados passam pela validação do modelo.
- A associação de eSIM e pacote utiliza o método `update()`.
- A atualização de atributos não exige reinserção da chave na árvore.

### Exceções

- ValueError: ID inválido, ID duplicado, dados inválidos, campo desconhecido ou tentativa de alterar o ID.
- LookupError: tentativa de atualizar cliente inexistente.
- OSError: falha de acesso ou gravação do arquivo.

### Persistência e integridade

A persistência está localizada em `globalsim/persistence/clients_json.py`.

- O JSON é carregado durante a inicialização do serviço.
- Os registros são armazenados no array na ordem de carregamento.
- A Árvore B é construída utilizando os IDs e as posições dos registros.
- O JSON armazena os registros completos, preservando a ordem do array.
- O JSON é atualizado após cada cadastro ou atualização bem-sucedida.
- A gravação utiliza arquivo temporário e substituição atômica.
- Em caso de falha, o serviço restaura a árvore, o array e as métricas anteriores.
- As operações públicas são protegidas por `RLock`.
- O bloqueio protege operações simultâneas sobre a mesma instância do serviço.
- Os registros retornados pelos métodos de consulta são cópias dos dados armazenados.
- Arquivos inválidos não são sobrescritos automaticamente.
- A árvore e os contadores não são armazenados diretamente no JSON.
- O índice é reconstruído após a reinicialização.

### Estatísticas da Árvore B

| Métrica | Descrição |
|---|---|
| size | Quantidade de clientes indexados |
| height | Quantidade de níveis da árvore |
| node_count | Quantidade de nós |
| splits | Quantidade de divisões de nós |
| lookups | Quantidade de chamadas válidas ao método público find() |

As chamadas ao método público `find()` realizadas durante atualizações também são contabilizadas.

A verificação interna de duplicidade durante uma inserção não incrementa o contador de buscas.

### Complexidade das operações do serviço

| Operação | Complexidade temporal |
|---|---|
| Busca por ID | O(log n) |
| Acesso ao registro pela posição | O(1) |
| Listagem completa | O(n) |
| Cadastro com persistência e rollback | O(n) |
| Atualização com persistência e rollback | O(n) |
| Armazenamento do array e do índice | O(n) de espaço |

A busca na Árvore B possui complexidade O(log n), considerando grau mínimo fixo.

O cadastro e a atualização possuem custo adicional linear devido às cópias utilizadas para rollback e à gravação completa do arquivo JSON.

### Limitações e integração

- A exclusão de clientes não está implementada.
- O serviço não permite alterar o ID de um cliente.
- A reorganização do array exigiria atualizar ou reconstruir o índice.
- O rollback utiliza cópias da árvore e do array, com custo adicional de tempo e memória proporcional à quantidade de registros.
- A existência do pacote no catálogo é verificada na interface Web quando um pacote é informado.
- O gerenciamento Web e o Planejador Multidestinos utilizam a interface pública do serviço.
- A integração com o Grafo permanece reservada para a Etapa 3.

### Testes automatizados

| Arquivo | Testes |
|---|---:|
| tests/test_b_tree.py | 31 |
| tests/test_client.py | 11 |
| tests/test_clients_json.py | 9 |
| tests/test_client_service.py | 36 |
| **Total** | **87** |

Os testes verificam as propriedades estruturais da árvore, as associações entre IDs e posições, o carregamento de 1.000 registros, a persistência, a validação, a atualização e o rollback.

Após a correção da Árvore B, a suíte completa do GlobalSIM foi executada com 240 testes aprovados em 27/11/2026.

## Checklist da correção da Árvore B — 27/11/2026

- [x] Separar armazenamento e indexação.
- [x] Utilizar o ID como chave da Árvore B.
- [x] Associar cada chave à posição do registro no array.
- [x] Preservar as associações durante as divisões.
- [x] Recuperar os registros por acesso direto ao array.
- [x] Preservar a ordenação lógica das listagens.
- [x] Preservar as posições durante atualizações.
- [x] Reconstruir o índice a partir dos registros persistidos.
- [x] Restaurar árvore, array e métricas em caso de falha.
- [x] Validar a estrutura com 1.000 clientes.
- [x] Preservar a integração com Flask e o Planejador Multidestinos.
- [x] Executar a suíte completa de testes sem falhas.