# Contratos implementados — entrega 1

Contratos da implementação inicial. Os nomes abaixo refletem a organização em inglês; as mensagens e os campos do enunciado permanecem em português.

## Checklist de implementação — atualizado em 07/10/2026

- [x] Modelo com campos obrigatórios, normalização e código imutável na edição.
- [x] Tabela Hash própria com inserção, busca, atualização, remoção e listagem.
- [x] Tratamento de colisões e instrumentação da estrutura.
- [x] Carga JSON na Hash durante a inicialização.
- [x] Consultas e mutações pelo serviço, usando a Hash.
- [x] Persistência após mutações e restauração do estado anterior em caso de falha.
- [x] Preservação do arquivo JSON inválido.
- [x] Rotas e templates integrados, com mutações por POST e redirecionamento 303.
- [x] Testes de integração com aplicação e arquivos temporários isolados.
- [ ] Revisão dos contratos.

## Etapa 1 — definir os dados

Adotar registros com `codigo`, `pais`, `regiao`, `operadora` e `tecnologia`. Normalizar o código com remoção de espaços externos e letras maiúsculas. Adotar duas letras ASCII como convenção. O código permanece imutável na edição. O modelo valida campos; o serviço verifica unicidade pela Hash.

## Etapa 2 — fechar a interface da Hash

| Operação implementada | Resultado |
|---|---|
| insert(record) | Inserir cópia do registro; sinalizar código duplicado |
| find(code) | Retornar cópia do registro ou ausência |
| update(code, record) | Alterar campos sem mudar a chave; sinalizar ausência |
| remove(code) | Retornar registro removido; sinalizar ausência |
| list_all() | Retornar cópias de todos os registros percorrendo os baldes |
| statistics() | Retornar capacidade, elementos, fator de carga, ocupação, colisões e último índice |

`insert` e `update` retornam `None` em caso de sucesso; `find` retorna um registro ou `None`; `remove` retorna o registro removido; `list_all` retorna uma lista; `statistics` retorna um dicionário de métricas. Duplicidade e troca de chave geram `ValueError`; atualização e remoção de chave ausente geram `LookupError`. A implementação usa vetor de baldes com listas para encadeamento separado, capacidade padrão de 17 e hash polinomial de base 31. Dicionários representam registros e métricas.

Contar uma colisão para cada inserção bem-sucedida em balde já ocupado. Duplicatas recusadas, buscas e atualizações não incrementam esse contador. Apresentar separadamente colisões de carga e de operações posteriores. A ocupação descreve o estado atual; a contagem acumulada descreve eventos. O fator de carga é elementos/capacidade e pode superar 1 com encadeamento.

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
