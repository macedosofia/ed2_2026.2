# GlobalSIM — Estruturas de Dados II

A Etapa 1 do GlobalSIM, desenvolvida para Estruturas de Dados II, é uma aplicação Web em Python e Flask para administrar países atendidos por uma empresa simulada de Internet móvel por eSIM.

O projeto está dividido em três etapas incrementais:

| Etapa | Estrutura principal | Funcionalidades |
|---|---|---|
| 1 | Tabela Hash | Gerenciamento de países e consulta de cobertura |
| 2 | Árvore B | Gerenciamento de clientes, eSIMs e pacotes |
| 3 | Grafo | Rede internacional e rotas de menor latência |

## 1. Etapa 1 — Tabela Hash e aplicação Web

**Prazo da entrega:** 20/10/2026

A aplicação utiliza uma Tabela Hash baseada no dicionário nativo (`dict`) do Python, com persistência em JSON e instrumentação. Nesta etapa estão disponíveis a página inicial, cadastro, consulta de cobertura, listagem, edição e remoção de países, além da validação de dados e mensagens de erro.

Cada país contém `codigo`, `pais`, `regiao`, `operadora` e `tecnologia`. O código de duas letras é normalizado e utilizado como chave, permanecendo imutável durante a edição.

## 2. Tecnologias

- Python 3.10 ou superior e Flask.
- HTML, CSS e templates Jinja.
- JSON para persistência e `unittest` para testes.
- Tabela Hash utilizando o `dict` do Python; Árvore B e Grafo previstos para implementação nas etapas seguintes.

## 3. Instalação e execução

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/macedosofia/ed2_2026.2.git
cd ed2_2026.2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app globalsim.app:create_app run --debug
```

Abra http://127.0.0.1:5000. Para parar o servidor, pressione `Ctrl+C`.

Os registros são carregados de `data/countries.json` para a Hash durante a inicialização. Consultas usam a estrutura em memória; operações bem-sucedidas persistem a lista obtida pela Hash. Um JSON inválido interrompe a inicialização sem ser sobrescrito.

A base inicial inclui os oito países de demonstração em `data/countries.json`. A cópia `data/countries.demo.json` permite restaurá-los; as instruções para preservar e recuperar a base estão em [Dados de países](data/README.md).

## 4. Organização do projeto

| Caminho | Responsabilidade |
|---|---|
| `app.py` | Fábrica Flask e inicialização |
| `models/country.py` | Validação e normalização |
| `structures/hash_table.py` | Tabela Hash baseada em `dict` e instrumentação |
| `services/countries.py` | Regras, operações e persistência |
| `persistence/countries_json.py` | Leitura e gravação atômica de JSON |
| `routes/countries.py` | Rotas HTTP e tratamento de erros |
| `templates/` e `static/` | Interface Web |
| `data/` | Bases de países |
| `tests/` | Testes automatizados |
| `../docs/` | Contratos, diferencial e roteiro de entrega |

## 5. Rotas

| Método | URL | Operação |
|---|---|---|
| GET | `/` | Página inicial |
| GET | `/countries` | Listagem |
| GET / POST | `/countries/new` | Formulário e cadastro |
| GET | `/coverage?codigo=BR` | Consulta de cobertura |
| GET / POST | `/countries/<code>/edit` | Formulário e atualização |
| POST | `/countries/<code>/delete` | Remoção |
| GET | `/instrumentation` | Métricas da Hash |

As consultas usam GET e as mutações usam POST com redirecionamento HTTP 303 após sucesso. Remoção por GET não é permitida.

## 6. Tabela Hash

A Tabela Hash utiliza o dicionário nativo (`dict`) do Python, que implementa internamente uma estrutura de dispersão. Os códigos dos países são utilizados como chaves, permitindo localizar diretamente os registros correspondentes. As operações de inserção, busca, atualização e remoção possuem complexidade O(1) em média, enquanto a listagem possui complexidade O(n).

A classe `HashTable` encapsula essas operações e mantém as métricas da estrutura. A página `/instrumentation` apresenta a quantidade de países cadastrados, registros carregados do JSON, buscas realizadas, buscas bem-sucedidas, buscas sem resultado, inserções, atualizações e remoções. Como o `dict` gerencia internamente seus baldes e colisões, essas informações não são contabilizadas diretamente pela aplicação.

## 7. Persistência

O serviço preserva o estado anterior da Hash e restaura registros e métricas se a gravação falhar. O módulo JSON grava em arquivo temporário e substitui o destino atomicamente. Os testes utilizam arquivos temporários para preservar os dados do projeto.

## 8. Testes

Execute na raiz do repositório, com o ambiente virtual ativado:

```bash
python -m unittest discover -s tests -v
```

Na entrega original de 20/10/2026, 25 testes foram aprovados.

Após a refatoração da Tabela Hash para `dict`, em 23/10/2026, foram executados **30 testes com sucesso**, utilizando Python 3.10.12 e Flask 3.1.3:

| Arquivo | Testes |
|---|---:|
| `../tests/test_country.py` | 4 |
| `../tests/test_country_service.py` | 5 |
| `../tests/test_demo.py` | 1 |
| `../tests/test_hash_table.py` | 6 |
| `../tests/test_persistence.py` | 5 |
| `../tests/test_routes.py` | 9 |
| **Total** | **30** |

Os testes verificam normalização, dados inválidos e duplicados, persistência Unicode, falhas de gravação e restauração do estado, cobertura dos oito países, operações da Tabela Hash, métricas renderizadas e reinicialização. Todos os cenários que alteram dados utilizam bases temporárias. Os testes cobrem os comportamentos descritos, sem afirmar ausência de todo defeito possível.

Consulte o [roteiro da entrega](../docs/delivery_1.md) para a demonstração.

## 9. Diferencial — planejador multidestinos com recomendação de pacotes eSIM

A equipe escolheu propor uma ferramenta para analisar destinos de viagem, duração e consumo estimado e recomendar um pacote eSIM com cobertura adequada. **A proposta foi submetida e aprovada pela professora.** A implementação do diferencial ocorrerá nas etapas seguintes.

A regra prevista é filtrar pacotes que cubram todos os destinos, tenham franquia suficiente e validade que cubra a duração da viagem. Entre os elegíveis, recomendar a menor franquia suficiente; em empates, considerar menor validade excedente e depois menor código. Os critérios finais serão confirmados pela equipe antes do desenvolvimento.

A Tabela Hash verificará cobertura, a Árvore B apoiará a gestão de clientes e eSIMs, e o Grafo calculará rotas de menor latência entre os trechos definidos pelo usuário. A ordem da viagem permanece definida pelo viajante.

### Limitações planejadas

- Um pacote para toda a viagem; sem combinar pacotes ou realizar compras.
- Operadoras fictícias, cobertura simulada e latências simuladas.
- Regras determinísticas, sem autenticação externa ou serviço de IA.

## 10. Cronograma

| Etapa | Prazo | Escopo |
|---|---|---|
| 1 — Tabela Hash | 20/10/2026 | Países, cobertura, persistência e interface Web |
| 2 — Árvore B | 24/11/2026 | Clientes, eSIMs, pacotes e recomendação inicial |
| 3 — Grafo | 01/12/2026 | Conectividade, BFS, DFS, Dijkstra e integração |

As etapas posteriores deverão preservar os recursos da primeira entrega.

## 11. Versionamento

O fluxo usa `main` para versões estáveis, `dev` para integração e branches próprias para funcionalidades, correções e documentação. Recomenda-se revisar as alterações, executar os testes e integrar por Pull Request.

A tag `etapa-1` preserva o marco anterior. A versão final da primeira entrega está identificada pela tag `etapa-1-final`. As refatorações posteriores são registradas em novos commits, preservando o histórico da entrega.

## 12. Checklist da primeira entrega

- [x] Tabela Hash, CRUD de países, instrumentação e persistência JSON.
- [x] Validação de dados e tratamento de erros.
- [x] Oito países de demonstração na base inicial.
- [x] Testes de modelo, serviço, rotas e persistência: 25 aprovados na entrega original.
- [x] Refatoração da Hash para `dict` e validação posterior: 30 testes aprovados.
- [x] Documentação técnica e roteiro de apresentação revisados.
- [x] Diferencial escolhido, descrito e aprovado pela professora.
- [x] Registrar o retorno da professora.
- [ ] Confirmar a submissão oficial pelo canal da disciplina, cujas instruções não constam no repositório.
- [ ] Confirmar a revisão cruzada e o ensaio de apresentação com a equipe.

A revisão técnica e os testes foram executados. O diferencial foi aprovado pela professora. A submissão acadêmica, a revisão entre integrantes e o ensaio continuam dependendo de confirmação da equipe.

## 13. Equipe

- Anderson de Jesus Soledade Filho
- João Cleber Freire Ramos Pinto
- Sofia Macêdo Costa
