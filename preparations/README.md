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

A aplicação implementa uma Tabela Hash própria com encadeamento separado, persistência em JSON e instrumentação. Nesta etapa estão disponíveis a página inicial, cadastro, consulta de cobertura, listagem, edição e remoção de países, além da validação de dados e mensagens de erro.

Cada país contém `codigo`, `pais`, `regiao`, `operadora` e `tecnologia`. O código de duas letras é normalizado e utilizado como chave, permanecendo imutável durante a edição.

## 2. Tecnologias

- Python 3.10 ou superior e Flask.
- HTML, CSS e templates Jinja.
- JSON para persistência e `unittest` para testes.
- Estruturas de dados implementadas pela equipe, sem substituição por bibliotecas prontas.

## 3. Instalação e execução

Clone o repositório e acesse a pasta da aplicação:

```bash
git clone https://github.com/macedosofia/ed2_2026.2.git
cd ed2_2026.2/preparations
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000. Para parar o servidor, pressione `Ctrl+C`.

Os registros são carregados de `data/countries.json` para a Hash durante a inicialização. Consultas usam a estrutura em memória; operações bem-sucedidas persistem a lista obtida pela Hash. Um JSON inválido interrompe a inicialização sem ser sobrescrito.

A base final inclui os oito países de demonstração em `data/countries.json`. A cópia `data/countries.demo.json` permite restaurá-los; as instruções para preservar e recuperar a base estão em [Dados de países](data/README.md).

## 4. Organização do projeto

| Caminho | Responsabilidade |
|---|---|
| `app.py` | Fábrica Flask e inicialização |
| `models/country.py` | Validação e normalização |
| `structures/hash_table.py` | Tabela Hash e instrumentação |
| `services/countries.py` | Regras, operações e persistência |
| `persistence/countries_json.py` | Leitura e gravação atômica de JSON |
| `routes/countries.py` | Rotas HTTP e tratamento de erros |
| `templates/` e `static/` | Interface Web |
| `data/` | Bases de países |
| `tests/` | Testes automatizados |
| `docs/` | Contratos, diferencial e roteiro de entrega |

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

A tabela usa um vetor de baldes, função polinomial de base 31, capacidade inicial de 17 e encadeamento por listas. A busca calcula o índice e percorre o balde correspondente. Com encadeamento, o fator de carga pode ultrapassar 1; as operações são O(1) em média e O(n) no pior caso.

Uma colisão é contada quando uma nova chave válida é inserida em um balde ocupado. A página `/instrumentation` apresenta capacidade, quantidade de países, fator de carga, ocupação, colisões da carga inicial e colisões posteriores. A ocupação mostra o estado atual; os contadores registram eventos acumulados.

## 7. Persistência

O serviço mantém uma cópia anterior da Hash e restaura registros e métricas se a gravação falhar. O módulo JSON grava em arquivo temporário e substitui o destino atomicamente. Os testes utilizam arquivos temporários para preservar os dados do projeto.

## 8. Testes

Execute dentro de `preparations`:

```bash
python -m unittest discover -s tests -v
```

Em 20/10/2026, 25 testes passaram com Python 3.12 e Flask 3.1.3:

| Arquivo | Testes |
|---|---:|
| `tests/test_country.py` | 4 |
| `tests/test_country_service.py` | 5 |
| `tests/test_demo.py` | 1 |
| `tests/test_hash_table.py` | 1 |
| `tests/test_persistence.py` | 5 |
| `tests/test_routes.py` | 9 |

Os testes verificam normalização, dados inválidos e duplicados, persistência Unicode, falhas de gravação e restauração do estado, cobertura dos oito países, colisão IT/DE, métricas renderizadas e reinicialização. Todos os cenários usam bases temporárias quando alteram dados. Os testes cobrem os comportamentos descritos, sem afirmar ausência de todo defeito possível.

Consulte o [roteiro da entrega](docs/delivery_1.md) para a demonstração.

## 9. Diferencial — planejador multidestinos com recomendação de pacotes eSIM

A equipe escolheu propor uma ferramenta para analisar destinos de viagem, duração e consumo estimado e recomendar um pacote eSIM com cobertura adequada. A proposta foi submetida à professora e aguarda aprovação. A implementação do diferencial ocorre nas etapas seguintes.

A regra prevista é filtrar pacotes que cubram todos os destinos, tenham franquia suficiente e validade que cubra a duração da viagem. Entre os elegíveis, recomendar a menor franquia suficiente; em empates, considerar menor validade excedente e depois menor código. Os critérios finais serão confirmados pela equipe antes do desenvolvimento.

A Tabela Hash verificará cobertura, a Árvore B apoiará a gestão de clientes e pacotes, e o Grafo calculará rotas de menor latência entre os trechos definidos pelo usuário. A ordem da viagem permanece definida pelo viajante.

### Limitações planejadas

- Um pacote para toda a viagem; sem combinar pacotes ou realizar compras.
- Operadoras fictícias, cobertura simulada e latências simuladas.
- Regras determinísticas, sem autenticação externa ou serviço de IA.

## 10. Cronograma

| Etapa | Prazo | Escopo |
|---|---|---|
| 1 — Tabela Hash | 20/10/2026 | Países, cobertura, persistência e interface Web |
| 2 — Árvore B | 10/11/2026 | Clientes, eSIMs, pacotes e recomendação inicial |
| 3 — Grafo | 01/12/2026 | Conectividade, BFS, DFS, Dijkstra e integração |

As etapas posteriores deverão preservar os recursos da primeira entrega.

## 11. Versionamento

O fluxo usa `main` para versões estáveis, `dev` para integração e branches próprias para funcionalidades, correções e documentação. Recomenda-se revisar as alterações, executar os testes e integrar por Pull Request.

A tag `etapa-1` preserva o marco anterior. A versão final da primeira entrega será marcada como `etapa-1-final` depois da publicação.

## 12. Checklist da primeira entrega

- [x] Tabela Hash, CRUD de países, instrumentação e persistência JSON.
- [x] Validação de dados e tratamento de erros.
- [x] Oito países de demonstração na base inicial.
- [x] Testes de modelo, serviço, rotas e persistência: 25 aprovados.
- [x] Documentação técnica e roteiro de apresentação revisados.
- [x] Diferencial escolhido, descrito e submetido à professora.
- [ ] Registrar o retorno da professora.
- [ ] Confirmar a submissão oficial pelo canal da disciplina, cujas instruções não constam no repositório.
- [ ] Confirmar a revisão cruzada e o ensaio de apresentação com a equipe.

A revisão técnica e os testes foram executados. A aprovação da professora, a submissão acadêmica, a revisão entre integrantes e o ensaio continuam dependendo de confirmação da equipe.

## 13. Equipe

- Anderson de Jesus Soledade Filho
- João Cleber Freire Ramos Pinto
- Sofia Macêdo Costa
