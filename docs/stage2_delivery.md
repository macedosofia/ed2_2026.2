# GlobalSIM — Entrega da Etapa 2

| Identificação | Informação |
|---|---|
| Disciplina | Estruturas de Dados II |
| Curso e instituição | Sistemas de Informação, Universidade do Estado da Bahia (UNEB) |
| Equipe | Anderson de Jesus Soledade Filho, João Cleber Freire Ramos Pinto e Sofia Macêdo Costa |
| Etapa e prazo | Etapa 2 — Árvore B e gerenciamento de clientes, 24/11/2026 |

A Etapa 2 amplia o GlobalSIM para gerenciar clientes, eSIMs e pacotes com uma Árvore B. O cadastro de países e as consultas de cobertura da Etapa 1 continuam disponíveis na Tabela Hash. A consulta cliente × destino e o Planejador Multidestinos integram as duas estruturas.

A referência do checklist é o enunciado `TrabalhoPratico-2026.2.pdf`. As páginas 4–6 especificam a Etapa 2. As páginas 2 e 9 definem as regras gerais e a persistência. A página 10 lista os critérios de avaliação e as responsabilidades na apresentação.

## Execução e testes

Use Python 3.10 ou superior. Na raiz do repositório, instale as dependências e inicie a aplicação.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app globalsim.app:create_app run
```

Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000).

Para preparar uma apresentação utilizando dados isolados, siga o [roteiro de demonstração](#roteiro-de-demonstração).

Execute a suíte na raiz, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -q
```

Na revisão `7951f69` da branch `dev`, após a integração dos PRs #18 e #19, a suíte completa passou com **225 testes automatizados**.

Os testes abrangem a Tabela Hash, a Árvore B, os serviços, a persistência em JSON, as rotas Flask, o Planejador Multidestinos e a geração da base demonstrativa.

A aplicação também foi verificada manualmente pelo navegador. O Planejador recebeu uma viagem com origem BR, destinos PT, FR e IT, duração de 25 dias e consumo de 8 GB, recomendando corretamente o pacote Europa Plus (102), com 10 GB e validade de 30 dias.

## Arquitetura e estruturas

[`create_app()`](../globalsim/app.py) inicializa os serviços com os arquivos de dados e registra os Blueprints de países, clientes e planejamento.

As [rotas](../globalsim/routes/) processam parâmetros e formulários, chamam os serviços e renderizam [templates Jinja](../globalsim/templates/).

Os [modelos](../globalsim/models/) validam e normalizam os registros.

Os [serviços](../globalsim/services/) coordenam as operações sobre as [estruturas em memória](../globalsim/structures/) e os módulos de [persistência](../globalsim/persistence/).

Os [testes](../tests/) exercitam estruturas, serviços, persistência e fluxos Flask com arquivos temporários.

```mermaid
flowchart TD
    Web["Flask e rotas"] --> Services["Serviços"]
    Services --> Hash["Tabela Hash de países"]
    Services --> BTree["Árvore B de clientes"]
    Services --> Packages["Catálogo de pacotes"]
    Services --> JSON["Leitura e gravação de JSON"]
    Web --> Views["Templates Jinja"]
```

### Tabela Hash

[`HashTable`](../globalsim/structures/hash_table.py) encapsula um `dict` do Python que guarda cada país pelo código de duas letras, como `IT`.

O [serviço de países](../globalsim/services/countries.py) normaliza o código, e a busca usa `dict.get()` sobre os dados carregados.

A estrutura permite inserir, consultar, atualizar, remover e listar registros. O código permanece imutável na edição.

A página `/instrumentation` mostra chaves, tamanho, registros carregados, buscas, acertos, buscas sem resultado e contadores de inserção, alteração e remoção.

O `dict` trata colisões internamente. A aplicação mede operações da Hash.

### Árvore B

[`BTree`](../globalsim/structures/b_tree.py) é uma árvore balanceada com várias chaves por nó e folhas no mesmo nível. Esse agrupamento reduz a quantidade de níveis que uma busca precisa percorrer.

Cada chave é o ID inteiro, positivo, único e imutável do cliente.

O grau mínimo `t` padrão é 3, o que permite até `2t − 1` chaves por nó, ou cinco. Um nó que fica abaixo da raiz tem pelo menos `t − 1` chaves.

- **Busca.** Compara o ID com as chaves do nó em ordem. Se encontrar uma igualdade, devolve uma cópia do registro. Caso contrário, desce pelo filho correspondente ao intervalo, ou retorna ausência ao chegar a uma folha.
- **Inserção.** Verifica se o ID já existe, divide a raiz cheia se necessário e, durante a descida, divide um filho cheio antes de entrar nele. A chave mediana e seu registro sobem para o pai, e as chaves restantes são repartidas em dois nós. Uma divisão da raiz acrescenta um nível.
- **Listagem e alteração.** O percurso em ordem visita cada filho intercalado com as chaves do nó e devolve os clientes em ordem crescente de ID. Na edição, o [serviço de clientes](../globalsim/services/clients.py) valida os campos e substitui o registro associado à mesma chave.
- **Métricas.** `/clients/instrumentation` mostra clientes, altura em níveis, quantidade de nós, divisões e buscas. As divisões feitas na carga também contam. O total de buscas inclui acertos, buscas sem resultado e chamadas a `find()` nas atualizações. A busca Web por um ID existente redireciona à tela de detalhes, que consulta o mesmo ID novamente.

### Persistência e catálogo

Na inicialização, `CountryService` e `ClientService` leem e validam os JSONs e inserem os registros nas estruturas.

Um arquivo de clientes ausente inicia a árvore vazia, e um JSON inválido interrompe a carga.

O [catálogo](../globalsim/services/packages.py) valida os pacotes uma vez e os mantém em um dicionário por código.

As consultas posteriores usam os serviços e os dados em memória.

Depois de uma mutação, os serviços de países e clientes gravam os registros completos em um arquivo temporário e substituem o destino atomicamente com `os.replace()`.

Se a operação falhar, restauram a cópia anterior da estrutura e das métricas.

O JSON guarda os registros. Na próxima inicialização, a árvore é reconstruída e os contadores são recalculados para a nova instância.

O enunciado permite armazenar os pacotes em JSON ou lista. O [catálogo simulado](../globalsim/data/packages.json) contém os cinco pacotes da tabela.

| Código | Pacote | Franquia | Validade | Países |
|---|---|---:|---:|---|
| 101 | Europa Basic | 5 GB | 15 dias | PT, ES, FR, IT |
| 102 | Europa Plus | 10 GB | 30 dias | PT, ES, FR, IT |
| 201 | América Basic | 5 GB | 15 dias | BR, US, CA |
| 202 | América Plus | 15 GB | 30 dias | BR, US, CA |
| 301 | Global | 20 GB | 30 dias | BR, PT, ES, FR, IT, US, CA, JP |

### Base demonstrativa de 1.000 clientes

A Etapa 2 inclui uma base demonstrativa versionada em [`globalsim/data/clients.demo.json`](../globalsim/data/clients.demo.json).

O arquivo contém 1.000 registros com IDs únicos de 1 a 1.000. Cada registro possui nome, e-mail, eSIM, pacote e status.

O [gerador](../scripts/generate_clients_demo.py) utiliza uma semente fixa para reproduzir o embaralhamento dos registros, permitindo carregar a Árvore B em uma ordem diferente da sequência crescente dos IDs.

A base apresenta:

- 1.000 IDs únicos.
- 800 clientes com eSIM.
- 200 clientes sem eSIM e sem pacote.
- Pacotes associados utilizando os códigos existentes no catálogo.
- Clientes ativos e inativos.
- Ordem de inserção embaralhada.
- E-mails demonstrativos no domínio `example.test`.

O carregamento é realizado pelo `ClientService`, utilizando a mesma implementação da Árvore B usada pela aplicação.

A [documentação específica](client_seed.md) apresenta o processo de geração, as proteções contra sobrescrita e os testes.

### Consulta cliente × país

Em [`/clients/coverage`](../globalsim/routes/clients.py), o ID localiza o cliente na Árvore B, e o código localiza o país na Tabela Hash.

O serviço de pacotes consulta o código associado ao cliente.

A tela mostra os dados das duas consultas e compara o destino com a lista de países do pacote.

A cobertura cadastrada depende da Hash. A compatibilidade é geográfica e independe do status do cliente.

### Planejador Multidestinos

O [Planejador Multidestinos com Recomendação Automática de Pacotes eSIM](differential.md) recebe a origem, os destinos em ordem, a duração, o consumo estimado e um ID de cliente opcional.

A origem é validada pelo formato. A Hash verifica a cobertura dos destinos, com códigos repetidos reduzidos à primeira ocorrência.

O [serviço](../globalsim/services/trip_planner.py) seleciona pacotes que abrangem todos os destinos e atendem à franquia e à validade.

Entre os elegíveis, prioriza a menor franquia suficiente, a menor validade excedente e, por último, o menor código.

A tela exibe a cobertura de cada destino, o pacote recomendado, quando houver, e a justificativa da seleção ou da ausência de opção.

A Árvore B localiza o cliente informado para mostrar o eSIM e o pacote atual.

A recomendação é consultiva e usa um único pacote simulado. A verificação de conectividade e de rotas por trecho fica para a Etapa 3.

## Checklist de requisitos e critérios de avaliação

| Enunciado | Implementação | Como verificar | Situação |
|---|---|---|---|
| Preservar a Etapa 1 e a Hash (p. 1, 3–6, 10) | [Hash](../globalsim/structures/hash_table.py), [rotas de países](../globalsim/routes/countries.py), [JSON de países](../globalsim/persistence/countries_json.py) | Demonstração 1 e [testes de rotas](../tests/test_routes.py). | Concluído e verificado |
| Árvore B funcional com ID único como chave, busca efetiva e divisões (p. 2, 4–6, 10) | [Árvore B](../globalsim/structures/b_tree.py), [modelo](../globalsim/models/client.py), [serviço](../globalsim/services/clients.py) | [Testes da Árvore B](../tests/test_b_tree.py), inclusive duplicatas, inserções e divisões. | Concluído e verificado |
| Carregar dados na Árvore B e trabalhar com centenas de clientes, recomendados cerca de 1.000 gerados automaticamente (p. 4–6, 9) | [Base de 1.000 clientes](../globalsim/data/clients.demo.json), [gerador](../scripts/generate_clients_demo.py), [ClientService](../globalsim/services/clients.py) | [Testes da base](../tests/test_client_seed.py), instrumentação e demonstração 3. | Concluído e verificado |
| Cadastro, busca, listagem e alteração (p. 5–6) | [Rotas de clientes](../globalsim/routes/clients.py), [serviço](../globalsim/services/clients.py) | Demonstração 2 e [testes das rotas](../tests/test_client_routes.py). | Concluído e verificado |
| Associação de eSIM e pacote ao cliente (p. 5) | [Formulário](../globalsim/templates/client_form.html), [validação Web](../globalsim/routes/clients.py), [catálogo](../globalsim/data/packages.json) | Edite um cliente e selecione o pacote. Confira o eSIM e o pacote nos detalhes e na consulta integrada. | Concluído e verificado |
| Persistência e consultas pelas estruturas em memória (p. 2, 5, 9) | [Persistência](../globalsim/persistence/), [serviços de países e clientes](../globalsim/services/) | Reinicie com os mesmos arquivos. Os [testes de clientes](../tests/test_client_service.py) e [de países](../tests/test_country_service.py) exercitam carga, consultas e falhas. | Concluído e verificado |
| Integração cliente × país e consulta ao catálogo (p. 5–6, 10) | [Rota integrada](../globalsim/routes/clients.py), [serviço de pacotes](../globalsim/services/packages.py) | Demonstração 4 e [testes das rotas](../tests/test_client_routes.py). | Concluído e verificado |
| Primeira versão funcional do diferencial aprovado (p. 2, 6, 10) | [Serviço](../globalsim/services/trip_planner.py), [Blueprint](../globalsim/routes/trip_planner.py), [fábrica Flask](../globalsim/app.py) | Demonstração 5 e [testes de integração](../tests/test_stage2_integration.py). | Concluído e verificado |
| Python/Flask, formulários HTML e Jinja, mutações por POST e estruturas separadas das rotas (p. 2, 10) | [Aplicação](../globalsim/app.py), [rotas](../globalsim/routes/), [templates](../globalsim/templates/), [estruturas](../globalsim/structures/) | Use os formulários e confira os redirecionamentos 303 após salvar com sucesso. | Concluído e verificado |
| Instrumentação da Hash e da Árvore B (p. 4, 10) | [Tela da Hash](../globalsim/templates/instrumentation.html), [tela da Árvore B](../globalsim/templates/client_instrumentation.html) | Compare métricas antes e depois das operações nas demonstrações 1 e 3. | Concluído e verificado |
| Repositório e README com equipe, execução, estruturas e diferencial (p. 10) | [README](../README.md), este guia | Confira a identificação e execute os comandos da raiz do repositório. | Preparado para revisão |
| Demonstração funcional e domínio de todos os integrantes (p. 10) | [Roteiro](#roteiro-de-demonstração) e [perguntas](#preparação-para-a-apresentação) | Cada integrante explica as estruturas, a ligação com Flask e a decisão do recomendador. | Roteiro pronto. Ensaio da equipe pendente |
| Grafo ponderado, BFS, DFS, Dijkstra, visualização e integração com a rede (p. 6–8, 10) | Escopo da entrega de 01/12/2026 | Demonstrar conectividade e rota de menor latência na entrega final. | Reservado para a Etapa 3 |

## Roteiro de demonstração

### Preparação

Para evitar modificar os arquivos permanentes do projeto, utilize cópias temporárias dos dados de países e clientes.

Na raiz do repositório, execute:

```bash
demo_dir="$(mktemp -d)"
cp globalsim/data/countries.demo.json "$demo_dir/countries.json"
cp globalsim/data/clients.demo.json "$demo_dir/clients.json"
```

Esses comandos criam uma base de demonstração separada dos arquivos principais.

O arquivo de clientes já contém os 1.000 registros demonstrativos.

Inicie o Flask utilizando os arquivos temporários:

```bash
python -m flask --app "globalsim.app:create_app({'COUNTRIES_PATH': '$demo_dir/countries.json', 'CLIENTS_PATH': '$demo_dir/clients.json'})" run
```

Abra [http://127.0.0.1:5000](http://127.0.0.1:5000).

Para demonstrar a persistência após reiniciar a aplicação, encerre o servidor com `Ctrl+C` e execute novamente o mesmo comando, reutilizando o diretório temporário.

### 1. Etapa 1 preservada

Abra `/` e `/countries`.

Em `/coverage?codigo=IT`, confira Itália, Europa e 5G.

Abra `/instrumentation`, cadastre `DE` em `/countries/new` com Alemanha, Europa, Operadora DE e 5G, e consulte a cobertura do novo país.

Edite a operadora ou remova DE pelo formulário de listagem.

Volte à instrumentação para observar as operações e confirme que IT continua disponível.

### 2. Gerenciamento de clientes

Abra `/clients`.

A base demonstrativa contém inicialmente 1.000 clientes.

Em `/clients/new`, cadastre o ID **58372** com nome **Cliente Demonstração**, e-mail `cliente.demo@example.test` e status `ativo`.

Esse é um registro de ensaio criado durante a apresentação, fora do intervalo de IDs da base original.

Após o cadastro, a aplicação deverá conter 1.001 clientes.

Busque o ID em `/clients/search?id=58372` e abra a edição para associar o eSIM `ESIM-DEMO-01` e o pacote **Europa Plus (102)**.

Reinicie a aplicação utilizando o mesmo diretório temporário e consulte `/clients/58372` para comprovar a persistência.

### 3. Carga e instrumentação com grande volume

Abra `/clients/instrumentation` logo após iniciar a aplicação, antes do cadastro do cliente de ensaio, para observar a carga inicial de **1.000 clientes**.

Confira a quantidade carregada, a altura, o número de nós e as divisões.

Na base demonstrativa versionada, os resultados documentados da carga são:

| Métrica | Resultado inicial |
|---|---:|
| Clientes | 1.000 |
| Altura | 5 |
| Nós | 315 |
| Divisões | 310 |
| Buscas | 0 |

Os valores podem mudar após inserções ou consultas realizadas durante a demonstração.

Em `/clients`, mostre que os registros aparecem em ordem crescente de ID, mesmo que a ordem de inserção original tenha sido embaralhada.

Busque um cliente existente, como o ID `1`.

Depois, busque um ID ausente, como `1001`, antes de cadastrar novos registros com esse identificador.

Volte à instrumentação para comparar o total de buscas.

A altura representa a quantidade de níveis da árvore. A contagem de nós representa as unidades estruturais, enquanto as divisões registram os desdobramentos realizados durante a inserção.

Se o cliente de ensaio `58372` já tiver sido cadastrado, a quantidade total será de 1.001 clientes.

A geração e a validação da base são explicadas em [Base demonstrativa de clientes](client_seed.md).

### 4. Consulta integrada

Abra `/clients/coverage?client_id=58372&codigo=IT` após criar o cliente da demonstração 2.

Confira a identificação, o eSIM e o pacote Europa Plus.

Mostre Itália, a operadora, a tecnologia 5G e a compatibilidade geográfica.

Em seguida, troque IT por JP para mostrar um país com cobertura cadastrada e fora do pacote Europa Plus.

A Árvore B localiza o cliente, a Hash localiza o país e a rota verifica a compatibilidade com os dados do catálogo.

### 5. Planejador

Abra `/trip-planner` pelo menu e informe:

- Origem: `BR`.
- Destinos: `PT, FR, IT`.
- Duração: `25` dias.
- Consumo estimado: `8` GB.

A tela deve mostrar cobertura nos três destinos e recomendar **Europa Plus (102)**, com **10 GB** e **30 dias** de validade.

O Europa Basic é insuficiente em franquia e validade.

O pacote Global também é elegível, mas possui franquia maior.

| Variação | Resultado para conferir |
|---|---|
| Acrescente `ZZ` aos destinos, mantendo o restante | A tela indica o destino sem cobertura cadastrada e encerra a seleção. |
| Mantenha o roteiro e use 21 GB | Os destinos têm cobertura. Nenhum pacote do catálogo tem franquia suficiente. |
| Informe o cliente `58372` da demonstração 2 | A tela mostra o eSIM e Europa Plus como pacote atual para comparação. |
| Informe um ID inexistente, como `99999` | O cliente aparece como inexistente e a recomendação para a viagem continua disponível. |

Mostre o caso principal e escolha uma variação.

Para evidenciar a integração com a Árvore B, utilize o cliente cadastrado durante a demonstração.

## Preparação para a apresentação

| Pergunta | Resposta curta |
|---|---|
| Por que usar uma Árvore B? | Um nó acomoda várias chaves ordenadas. O balanceamento limita a altura e permite buscar um ID descendo apenas pelo intervalo correspondente. |
| O que é grau mínimo e quando se divide um nó? | Com `t = 3`, cada nó suporta até cinco chaves. A inserção divide um nó cheio antes de descer e sobe a chave mediana ao pai. |
| Por que a listagem ordena os IDs? Qual a diferença entre altura e nós? | O percurso em ordem intercala filhos e chaves. A altura conta os níveis entre raiz e folhas, e a contagem de nós soma os nós da estrutura. |
| Como localizar um país e o que acontece com um código ausente? | O código normalizado é a chave em um `dict`. A busca média é O(1). Uma chave ausente retorna `None` e conta como busca sem resultado. |
| Como Flask usa as estruturas? | A fábrica inicializa os serviços e os Blueprints. As rotas chamam os serviços compartilhados, e os templates renderizam os resultados. |
| Por que JSON e o que acontece no reinício ou em caso de falha? | O enunciado permite JSON para guardar os registros. A inicialização reconstrói a Hash e a Árvore B, que atendem às buscas. Se a gravação falhar, o serviço restaura a estrutura e seus contadores. |
| Por que usar duas estruturas? Qual o papel do catálogo? | A Hash atende à consulta direta por código. A Árvore B consulta IDs e devolve os clientes em ordem. O catálogo recupera por código o pacote associado e fornece seus países e limites. |
| Como a recomendação é escolhida? Por que é determinística e dispensa IA? | Regras explícitas filtram cobertura, franquia e validade. A menor franquia, a menor validade excedente e o menor código resolvem a escolha com o mesmo resultado para os mesmos dados. |
| O que a tela mostra sem uma opção compatível? | Se um destino estiver ausente da Hash, a tela identifica o destino sem cobertura. Se todos estiverem cobertos, ela informa que o catálogo não atende à viagem. |
| O que o Grafo acrescentará? | A rede simulada terá países como vértices e conexões ponderadas por latência. BFS e DFS percorrem a rede, e Dijkstra calcula a rota de menor latência por trecho. |

## Pendências da entrega

- Validar a demonstração da base de 1.000 clientes no Flask, utilizando os arquivos temporários e conferindo a instrumentação.
- Ensaiar o roteiro com todos os integrantes da equipe.
- Confirmar a submissão do projeto pelo canal definido pela professora.

A implementação funcional e os testes automatizados da Etapa 2 estão concluídos. A conectividade por Grafo permanece reservada para a Etapa 3.