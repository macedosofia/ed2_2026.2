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
