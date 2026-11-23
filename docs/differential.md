# Diferencial GlobalSIM — Planejador Multidestinos com Recomendação Automática de Pacotes eSIM

**Status:** Escolhido pela equipe e aprovado pela professora.

**Etapa atual:** Etapa 2, com recomendador funcional e Blueprint testado. O registro na aplicação principal está pendente de integração.

## 1. Visão geral

O diferencial escolhido pela equipe consiste no desenvolvimento de um Planejador Multidestinos com Recomendação Automática de Pacotes eSIM.

O usuário informa os países que pretende visitar, a duração da viagem e o consumo estimado de dados móveis. O GlobalSIM consulta a cobertura cadastrada nos destinos e, quando há uma opção elegível, recomenda um pacote para todo o roteiro.

O diferencial será desenvolvido de maneira incremental, utilizando a
Tabela Hash, a Árvore B e o Grafo implementados nas respectivas etapas
do projeto.

## 2. Problema a ser resolvido

Viajantes internacionais podem encontrar dificuldades para selecionar um pacote eSIM adequado, especialmente quando pretendem visitar múltiplos países.

A escolha de um pacote exige considerar diferentes fatores:

- Cobertura disponível nos países de destino.
- Quantidade de dados móveis necessária.
- Duração total da viagem.
- Franquia e validade dos pacotes disponíveis.

A consulta individual de cobertura não é suficiente para identificar automaticamente qual pacote atende a todas essas condições.

Assim, o planejador busca auxiliar o usuário na escolha de um pacote compatível com seu roteiro, apresentando uma recomendação baseada em critérios objetivos.

## 3. Funcionalidades da Etapa 2

O planejador permite as seguintes operações.

1. Informar múltiplos países de destino.
2. Informar a duração total da viagem, em dias.
3. Informar o consumo estimado de Internet, em GB.
4. Verificar a cobertura disponível em cada país informado.
5. Identificar os pacotes compatíveis com todos os destinos.
6. Comparar a franquia e a validade dos pacotes elegíveis.
7. Recomendar um pacote que atenda às necessidades informadas.
8. Apresentar uma justificativa para a recomendação.
9. Informar quando não existir um pacote compatível.
10. Consultar um cliente por ID e mostrar seu eSIM e pacote atual para comparação.

## 4. Entradas e saídas

### 4.1. Entradas

O serviço recebe as instâncias por `TripPlannerService(country_service, package_service, client_service=None)` e expõe `recommend(origin, destinations, duration_days, data_gb, client_id=None)`.

| Campo | Entrada no serviço | Exemplo |
|---|---|---|
| Origem | Código de duas letras de A a Z | `"BR"` |
| Destinos | Lista ou tupla ordenada com pelo menos um código | `["PT", "FR", "IT"]` |
| Duração | Inteiro positivo em dias | `25` |
| Consumo | `int`, `float` ou `Decimal` positivo e finito, em GB | `Decimal("8.5")` |
| ID do cliente | Inteiro positivo ou `None` | `58372` |

O planejador remove espaços externos dos códigos e os converte em maiúsculas. Entre destinos duplicados, mantém a primeira ocorrência. A origem é validada pelo formato e incluída no resultado. A exigência de cobertura do pacote aplica-se aos destinos.

O formulário separa destinos por vírgulas e converte os números antes de chamar o serviço. O consumo aceita `8,5` e `8.5` no formulário. A conversão para `Decimal` preserva a parte fracionária para a comparação com a franquia. Valores booleanos são inválidos nos campos numéricos.

### 4.2. Saídas

Entradas inválidas geram `ValueError` antes da consulta aos serviços. Para uma viagem válida, o serviço devolve um dicionário com os seguintes campos.

| Campos | Conteúdo |
|---|---|
| `origem`, `duracao_dias`, `consumo_gb` | Origem normalizada, duração e consumo em `Decimal` |
| `destinos`, `destinos_sem_cobertura` | Destinos ordenados com `codigo`, `pais` (quando disponível) e `cobertura` booleana. A segunda lista contém os códigos sem cobertura. |
| `status` | `recomendado`, `sem_cobertura` ou `sem_pacote` |
| `pacote_recomendado`, `justificativa` | Pacote selecionado (ou `None`) e explicação do resultado |
| `cliente_id`, `status_cliente` | ID informado e situação da consulta. Os valores são `nao_informado`, `encontrado`, `nao_encontrado` ou `consulta_indisponivel`. |
| `cliente`, `pacote_atual` | Dados do cliente e pacote associado, quando encontrados. Os campos indisponíveis recebem `None`. |

O status da viagem independe do status da consulta ao cliente. Um ID inexistente é informado no resultado da viagem, e `consulta_indisponivel` indica que a instância foi configurada sem serviço de clientes.

## 5. Algoritmo de recomendação

O sistema filtra e seleciona os pacotes com um algoritmo determinístico em Python e usa os dados já disponíveis no GlobalSIM.

### 5.1. Validação dos destinos

Após validar a viagem, o serviço chama `CountryService.find(codigo)` para cada destino normalizado. Se faltar cobertura em qualquer destino, o resultado lista todos os códigos ausentes e encerra a seleção com `sem_cobertura`.

### 5.2. Filtragem dos pacotes

Com todos os destinos cadastrados, o planejador usa o catálogo retornado por `PackageService.list_all()`. Um pacote é elegível quando satisfaz as três condições a seguir.

1. Oferecer cobertura para todos os destinos informados.
2. Possuir franquia de dados maior ou igual ao consumo estimado.
3. Possuir validade maior ou igual à duração total da viagem.

### 5.3. Seleção do pacote recomendado

Entre os pacotes elegíveis, o planejador escolhe o mínimo pela seguinte ordem de prioridade.

1. Menor franquia de dados que ainda atenda ao consumo estimado.
2. Menor validade excedente em relação à duração da viagem.
3. Menor código identificador do pacote, em caso de empate.

Em uma passagem pelos candidatos do catálogo, `min()` compara a chave `(dados_gb, validade_dias - duracao_dias, codigo)`. A recomendação independe da ordem do catálogo. A justificativa informa o pacote, os destinos cobertos, a franquia, o consumo estimado, a validade, a duração e os critérios usados na escolha.

### 5.4. Ausência de pacote compatível

Se os destinos tiverem cobertura, mas nenhum pacote atender ao roteiro, o resultado é `sem_pacote` e inclui a mensagem de ausência de opção compatível.

### 5.5. Dados dos pacotes

O serviço de pacotes carrega o catálogo em `globalsim/data/packages.json`, com código, nome, franquia, validade e lista de países. Os pacotes Europa cobrem PT, ES, FR e IT. Os pacotes América cobrem BR, US e CA. O Global cobre os oito países da base. O catálogo simula disponibilidade e inclui apenas os campos usados pela aplicação.

## 6. Exemplo de funcionamento

O exemplo usa Brasil como origem, Portugal, França e Itália como destinos, 25 dias de viagem e consumo estimado de 8 GB. Execute a partir da raiz do repositório.

```python
from globalsim.services.countries import CountryService
from globalsim.services.packages import PackageService
from globalsim.services.trip_planner import TripPlannerService

planner = TripPlannerService(CountryService("globalsim/data/countries.json"), PackageService())
result = planner.recommend("BR", ["PT", "FR", "IT"], 25, 8)
package = result["pacote_recomendado"]
print(package["codigo"], package["nome"])
print(result["justificativa"])
```

### 6.1. Verificação de cobertura

Na base atual, os três destinos constam na Tabela Hash.

| País | Cobertura |
|---|---|
| Portugal | Disponível |
| França | Disponível |
| Itália | Disponível |

### 6.2. Comparação dos pacotes

Europa Basic, Europa Plus e Global oferecem cobertura nos três destinos do exemplo.

| Pacote | Dados | Validade | Elegível |
|---|---|---|---|
| Europa Basic | 5 GB | 15 dias | Não |
| Europa Plus | 10 GB | 30 dias | Sim |
| Global | 20 GB | 30 dias | Sim |

O pacote Europa Basic não atende à franquia e à validade necessárias.

Os pacotes Europa Plus e Global atendem aos requisitos.

### 6.3. Resultado da recomendação

**Pacote recomendado — Europa Plus (102)**

Os três destinos são atendidos por 10 GB com validade de 30 dias. Essa é a menor franquia entre os pacotes elegíveis para o exemplo.

## 7. Integração com as estruturas de dados

### 7.1. Etapa 1 — Tabela Hash

O `CountryService.find()` consulta os registros da Tabela Hash já carregada em memória. Cada destino distinto gera uma busca e é incluído no resultado, inclusive quando falta cobertura.

### 7.2. Etapa 2 — Árvore B

Com um ID informado e o serviço de clientes configurado, o planejador usa `ClientService.find()`, que busca o cliente na Árvore B. Se o registro tiver um código de pacote associado, `PackageService.find()` recupera o pacote atual para comparação com a recomendação. O formulário informa quando faltam eSIM, associação ou registro do pacote no catálogo. A busca tem o mesmo comportamento para clientes ativos e inativos.

O planejador acessa os serviços por operações de leitura. Os registros de países, clientes e pacotes são preservados, assim como seus arquivos JSON.

### 7.3. Etapa 3 — Grafo (previsto)

O Grafo representará a rede internacional simulada do GlobalSIM,
com países como vértices e conexões como arestas ponderadas.

Os pesos representarão as latências simuladas das conexões.

O planejador utilizará o algoritmo de Dijkstra para calcular rotas de menor latência entre os destinos informados pelo usuário.

A ordem dos países será definida pelo roteiro do usuário.

O sistema calculará a conectividade para cada trecho do roteiro, sem tentar otimizar a ordem de visitação dos países.

Caso não exista caminho entre dois destinos, o sistema deverá informar a indisponibilidade de conectividade naquele trecho.

A verificação de cobertura e a existência de caminhos no Grafo serão tratadas como informações distintas.

### 7.4. Registro do Blueprint

O Blueprint atende a `GET /trip-planner` e `POST /trip-planner`. O GET exibe o formulário e o POST apresenta o resultado na mesma página. Entradas inválidas recebem HTTP 400. Consultas válidas, incluindo as sem recomendação, recebem HTTP 200.

O registro definitivo em `create_app()` e o link no menu ficam para a integração com a interface de clientes. Após a revisão, a fábrica poderá montar `TripPlannerService(app.extensions["countries"], package_service, client_service)` com as instâncias existentes e registrar `create_trip_planner_blueprint(planner)` antes de retornar a aplicação. O endpoint do link é `trip_planner.plan_trip`.

Para uma demonstração local do formulário, execute o exemplo abaixo em Python a partir da raiz do repositório e abra `http://127.0.0.1:5000/trip-planner`. Esse exemplo usa o modo de recomendação sem consulta de cliente. Os testes do Blueprint exercitam o mesmo formulário com um serviço de clientes e dados temporários.

```python
from globalsim.app import create_app
from globalsim.routes.trip_planner import create_trip_planner_blueprint
from globalsim.services.packages import PackageService
from globalsim.services.trip_planner import TripPlannerService

app = create_app()
planner = TripPlannerService(app.extensions["countries"], PackageService())
app.register_blueprint(create_trip_planner_blueprint(planner))
app.run()
```

## 8. Diferencial em relação aos requisitos obrigatórios

O enunciado prevê consultas individuais de cobertura e uma consulta integrada entre cliente, país, pacote e rede.

Na Etapa 2, o diferencial amplia a consulta individual de cobertura em cinco operações.

- Analisar múltiplos destinos em uma única operação.
- Considerar a duração e o consumo estimado de uma viagem.
- Comparar diferentes pacotes eSIM.
- Selecionar automaticamente um pacote compatível.
- Justificar a recomendação utilizando critérios objetivos.

A conectividade entre os trechos é parte da Etapa 3. A cobertura de cada destino e os dados do cliente já usam a Tabela Hash e a Árvore B, respectivamente.

## 9. Escopo e limitações

A primeira versão é consultiva e recomenda um único pacote do catálogo simulado para toda a viagem. O roteiro segue a ordem informada pelo viajante após a normalização. Compra, pagamento, combinação de pacotes e consulta a operadoras reais ficam fora do escopo. A conectividade da rede segue o planejamento da Etapa 3.

## 10. Critérios de aceite

Os testes da Etapa 2 exercitam a validação de entradas, a cobertura, a escolha do pacote, a busca de cliente e a preservação dos registros.

| Cenário | Resultado esperado |
|---|---|
| Todos os destinos possuem cobertura | Prosseguir com a análise dos pacotes |
| Destino sem cobertura cadastrada | Informar o destino não atendido |
| Pacote com dados insuficientes | Descartar o pacote |
| Pacote com validade insuficiente | Descartar o pacote |
| Pacote sem cobertura em todos os destinos | Descartar o pacote |
| Dois ou mais pacotes elegíveis | Aplicar os critérios de seleção |
| Nenhum pacote elegível | Informar ausência de recomendação |
| Cliente cadastrado na Árvore B | Recuperar seus dados |
| Cliente inexistente | Informar que não foi encontrado |
| Entrada inválida | Informar o campo inválido e apresentar HTTP 400 na Web |
| Rota existente no Grafo (Etapa 3) | Apresentar caminho e latência |
| Rota inexistente no Grafo (Etapa 3) | Informar ausência de conectividade |

Os testes de `tests/test_trip_planner.py` usam os serviços sobre arquivos temporários. Eles verificam a seleção com diferentes ordens do catálogo, os contadores de buscas na Hash e na Árvore B e a integridade dos registros e arquivos. `tests/test_trip_planner_routes.py` registra o Blueprint em uma instância de teste do Flask e usa `app.test_client()` para verificar GET e POST.

Com as dependências de `requirements.txt` instaladas, execute a suíte completa.

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -q
```

## 11. Cronograma de implementação

| Etapa | Entrega prevista | Prazo |
|---|---|---|
| 1 | Documentação do diferencial e integração planejada | 20/10/2026 |
| 2 | Recomendador funcional e integração com clientes | 24/11/2026 |
| 3 | Integração com Grafo e conectividade do roteiro | 01/12/2026 |

## 12. Decisão da equipe

**Diferencial escolhido:**
Planejador Multidestinos com Recomendação Automática de Pacotes eSIM.

**Situação da decisão:**
Escolha confirmada internamente pela equipe.

**Justificativa:**
A proposta apresenta uma aplicação prática para o GlobalSIM, permite integrar as três estruturas de dados exigidas pela disciplina e possui complexidade compatível com o prazo de desenvolvimento.

**Alternativa de reserva:**
A definir, caso seja solicitada uma alternativa pela professora.

**Responsáveis:**
A distribuição específica das atividades do diferencial será confirmada pela equipe, respeitando o cronograma geral do projeto.

**Submissão à professora:**
Proposta enviada em outubro de 2026.

**Aprovação da professora:**
Proposta aprovada pela professora.

**Situação da implementação:**
Recomendador, consulta opcional de cliente e Blueprint implementados para a Etapa 2. O registro na aplicação principal será feito na integração. A conectividade do roteiro está prevista para a Etapa 3.

## 13. Checklist de acompanhamento

### Definição

- [x] Documentar uma proposta inicial de recomendação de pacotes.
- [x] Descrever o problema, as entradas e as saídas esperadas.
- [x] Descrever a integração com Hash, Árvore B e Grafo.
- [x] Registrar cenários iniciais de teste.
- [x] Confirmar o diferencial escolhido pela equipe.
- [x] Registrar a decisão e justificar sua relevância.
- [x] Definir um escopo mínimo sem dependências externas obrigatórias.
- [x] Registrar os critérios de recomendação e desempate adotados na Etapa 2.
- [x] Definir a cobertura geográfica no catálogo de pacotes.
- [ ] Definir a alternativa de reserva, se necessária.
- [ ] Registrar a divisão de responsabilidades.

### Entrega da Etapa 1

- [x] Escolher o diferencial da equipe.
- [x] Documentar o problema e a solução proposta.
- [x] Descrever a integração com Hash, Árvore B e Grafo.
- [x] Submeter a proposta à professora.
- [x] Incorporar a descrição do diferencial ao README.
- [x] Integrar a documentação inicial à branch dev.
- [x] Registrar a aprovação da professora.
- [ ] Atualizar o documento caso a professora solicite alterações.

### Entrega da Etapa 2

- [x] Implementar o algoritmo de recomendação.
- [x] Implementar e testar o formulário de planejamento.
- [x] Integrar a consulta de cobertura pela Hash.
- [x] Integrar a consulta opcional de cliente pela Árvore B.
- [x] Atualizar a documentação da Etapa 2.
- [ ] Registrar o Blueprint e o link de navegação na aplicação principal.

### Etapa 3

- [ ] Integrar as rotas de menor latência pelo Grafo.
- [ ] Atualizar a documentação final.

## 14. Observações

As regras e os exemplos documentados representam a implementação da Etapa 2. Ajustes acordados na revisão devem ser registrados pela equipe.

A prioridade do projeto continuará sendo a implementação correta das estruturas de dados obrigatórias e sua integração com Flask.
