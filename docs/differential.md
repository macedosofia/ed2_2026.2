# Diferencial GlobalSIM — Planejador Multidestinos com Recomendação Automática de Pacotes eSIM

**Status:** Escolhido pela equipe e aprovado pela professora.

**Etapa atual:** Etapa 1 — Definição e documentação do diferencial.

## 1. Visão geral

O diferencial escolhido pela equipe consiste no desenvolvimento de um Planejador Multidestinos com Recomendação Automática de Pacotes eSIM.

A funcionalidade permitirá que o usuário informe os países que pretende visitar, a duração total da viagem e o consumo estimado de dados móveis.

Com base nessas informações, o GlobalSIM verificará a disponibilidade de cobertura nos destinos e recomendará um pacote de Internet compatível com as necessidades informadas.

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

## 3. Funcionalidades previstas

O planejador deverá permitir:

1. Informar múltiplos países de destino.
2. Informar a duração total da viagem, em dias.
3. Informar o consumo estimado de Internet, em GB.
4. Verificar a cobertura disponível em cada país informado.
5. Identificar os pacotes compatíveis com todos os destinos.
6. Comparar a franquia e a validade dos pacotes elegíveis.
7. Recomendar um pacote que atenda às necessidades informadas.
8. Apresentar uma justificativa para a recomendação.
9. Informar quando não existir um pacote compatível.

Nas etapas seguintes, a funcionalidade também permitirá consultar os dados do cliente e apresentar informações de conectividade da rede internacional simulada.

## 4. Entradas e saídas

### 4.1. Entradas

O usuário deverá informar:

| Campo | Descrição | Exemplo |
|---|---|---|
| Origem | País de origem da viagem | BR |
| Destinos | Lista ordenada de países a visitar | PT, FR, IT |
| Duração | Duração total da viagem, em dias | 25 |
| Consumo | Consumo estimado de Internet, em GB | 8 |

Na integração com a Etapa 2, também poderá ser informado o identificador do cliente para recuperar seus dados na Árvore B.

### 4.2. Saídas

O sistema deverá apresentar:

- Os destinos informados pelo usuário.
- A disponibilidade de cobertura em cada destino.
- O pacote eSIM recomendado, quando houver.
- A franquia de dados do pacote.
- O período de validade do pacote.
- Uma justificativa objetiva para a recomendação.
- Mensagens informativas quando não houver cobertura ou pacote compatível.

Na integração com a Etapa 3, o sistema também apresentará as rotas de menor latência calculadas na rede simulada.

## 5. Algoritmo de recomendação

O sistema utilizará um algoritmo determinístico de filtragem e seleção de pacotes, implementado pela equipe em Python.

A recomendação não dependerá de serviços externos ou modelos de inteligência artificial.

### 5.1. Validação dos destinos

Inicialmente, os códigos dos países serão normalizados e consultados na Tabela Hash.

Caso algum destino não possua cobertura cadastrada, o sistema informará quais países não são atendidos.

Não será recomendado um pacote como compatível com todo o roteiro quando existirem destinos sem cobertura.

### 5.2. Filtragem dos pacotes

Para ser considerado elegível, um pacote deverá:

1. Oferecer cobertura para todos os destinos informados.
2. Possuir franquia de dados maior ou igual ao consumo estimado.
3. Possuir validade maior ou igual à duração total da viagem.

Pacotes que não atenderem a qualquer uma dessas condições serão descartados da recomendação.

### 5.3. Seleção do pacote recomendado

Entre os pacotes elegíveis, propõe-se utilizar os seguintes critérios,
em ordem de prioridade:

1. Menor franquia de dados que ainda atenda ao consumo estimado.
2. Menor validade excedente em relação à duração da viagem.
3. Menor código identificador do pacote, em caso de empate.

Esses critérios tornam a recomendação previsível e reproduzível.

A equipe deverá confirmar os critérios antes da implementação.

### 5.4. Ausência de pacote compatível

Caso nenhum pacote satisfaça os requisitos informados, o sistema deverá apresentar uma mensagem explicando que não existe uma opção compatível.

O sistema não deverá recomendar um pacote insuficiente apenas para apresentar um resultado.

### 5.5. Dados dos pacotes

Os pacotes poderão ser armazenados em JSON, conforme permitido pelo enunciado.

Além das informações de código, nome, franquia e validade, será necessário definir explicitamente a cobertura geográfica de cada pacote.

A relação dos países cobertos deverá ser estabelecida pela equipe antes da implementação do recomendador.

Não serão utilizados critérios de menor preço, pois os pacotes
apresentados no enunciado não possuem valores definidos.

## 6. Exemplo de funcionamento

Considere o seguinte roteiro:

**País de origem:** Brasil

**Destinos:**
- Portugal (PT)
- França (FR)
- Itália (IT)

**Duração:** 25 dias

**Consumo estimado:** 8 GB

### 6.1. Verificação de cobertura

O sistema consultará a Tabela Hash para verificar se os destinos
possuem cobertura disponível.

Considerando que os três países estejam cadastrados, o resultado será:

| País | Cobertura |
|---|---|
| Portugal | Disponível |
| França | Disponível |
| Itália | Disponível |

### 6.2. Comparação dos pacotes

Para fins de exemplo, considera-se que os pacotes Europa Basic, Europa Plus e Global oferecem cobertura nos três destinos.

| Pacote | Dados | Validade | Elegível |
|---|---|---|---|
| Europa Basic | 5 GB | 15 dias | Não |
| Europa Plus | 10 GB | 30 dias | Sim |
| Global | 20 GB | 30 dias | Sim |

O pacote Europa Basic não atende à franquia e à validade necessárias.

Os pacotes Europa Plus e Global atendem aos requisitos.

### 6.3. Resultado da recomendação

**Pacote recomendado: Europa Plus**

- Dados disponíveis: 10 GB.
- Validade: 30 dias.
- Destinos atendidos: Portugal, França e Itália.

**Justificativa:**

O pacote Europa Plus atende aos três destinos informados, possui franquia suficiente para o consumo estimado de 8 GB e validade adequada para os 25 dias de viagem.

Entre os pacotes elegíveis do exemplo, apresenta a menor franquia de dados suficiente.

Este exemplo considera uma cobertura geográfica proposta para os pacotes, que deverá ser confirmada pela equipe.

## 7. Integração com as estruturas de dados

### 7.1. Etapa 1 — Tabela Hash

A Tabela Hash será responsável por armazenar e consultar os países atendidos pelo GlobalSIM.

No planejador, ela será utilizada para verificar a disponibilidade de cobertura de cada destino informado.

As consultas deverão utilizar a estrutura Hash carregada em memória, sem realizar buscas diretamente no arquivo JSON.

Na entrega da Etapa 1, será apresentada a especificação inicial do diferencial e sua integração prevista com a estrutura.

### 7.2. Etapa 2 — Árvore B

A Árvore B será responsável pelo armazenamento e pela consulta dos registros de clientes, utilizando seus identificadores como chave.

O planejador poderá recuperar os dados de um cliente e identificar seu pacote atual.

Com isso, será possível comparar o pacote associado ao cliente com a recomendação gerada para a viagem.

Nessa etapa, está prevista a implementação do núcleo funcional do recomendador, incluindo:

- Formulário para planejamento da viagem.
- Consulta de cobertura dos destinos.
- Filtragem dos pacotes disponíveis.
- Seleção e justificativa do pacote recomendado.
- Integração com os dados dos clientes.

### 7.3. Etapa 3 — Grafo

O Grafo representará a rede internacional simulada do GlobalSIM,
com países como vértices e conexões como arestas ponderadas.

Os pesos representarão as latências simuladas das conexões.

O planejador utilizará o algoritmo de Dijkstra para calcular rotas de menor latência entre os destinos informados pelo usuário.

A ordem dos países será definida pelo roteiro do usuário.

O sistema calculará a conectividade para cada trecho do roteiro, sem tentar otimizar a ordem de visitação dos países.

Caso não exista caminho entre dois destinos, o sistema deverá informar a indisponibilidade de conectividade naquele trecho.

A verificação de cobertura e a existência de caminhos no Grafo serão tratadas como informações distintas.

## 8. Diferencial em relação aos requisitos obrigatórios

O enunciado prevê consultas individuais de cobertura e uma consulta integrada entre cliente, país, pacote e rede.

O diferencial acrescentará a possibilidade de:

- Analisar múltiplos destinos em uma única operação.
- Considerar a duração e o consumo estimado de uma viagem.
- Comparar diferentes pacotes eSIM.
- Selecionar automaticamente um pacote compatível.
- Justificar a recomendação utilizando critérios objetivos.
- Apresentar a conectividade da rede para os trechos do roteiro.

Assim, o planejador amplia as funcionalidades obrigatórias sem substituir as estruturas de dados exigidas pela disciplina.

## 9. Escopo e limitações

Para manter a implementação viável, a primeira versão do diferencial terá as seguintes limitações:

- Será recomendado apenas um pacote para toda a viagem.
- Não serão combinados múltiplos pacotes.
- Não haverá compra ou pagamento de pacotes.
- Não serão consultadas operadoras reais.
- Não será necessário login com Google.
- Não haverá dependência obrigatória de LLMs ou APIs externas.
- A recomendação será baseada em regras determinísticas.
- As latências serão simuladas, conforme o modelo do Grafo.
- A ordem dos destinos será informada pelo usuário.

Funcionalidades adicionais poderão ser consideradas apenas após a conclusão e validação dos requisitos obrigatórios.

## 10. Critérios de aceite

A funcionalidade será considerada adequada quando os seguintes cenários forem atendidos:

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
| Rota existente no Grafo | Apresentar caminho e latência |
| Rota inexistente no Grafo | Informar ausência de conectividade |

Os testes serão implementados progressivamente, acompanhando as etapas correspondentes.

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
A implementação do diferencial está prevista para as Etapas 2 e 3, após a definição final do escopo.

## 13. Checklist de acompanhamento

### Definição

- [x] Documentar uma proposta inicial de recomendação de pacotes.
- [x] Descrever o problema, as entradas e as saídas esperadas.
- [x] Descrever a integração com Hash, Árvore B e Grafo.
- [x] Registrar cenários iniciais de teste.
- [x] Confirmar o diferencial escolhido pela equipe.
- [x] Registrar a decisão e justificar sua relevância.
- [x] Definir um escopo mínimo sem dependências externas obrigatórias.
- [ ] Confirmar os critérios de recomendação e desempate com a equipe.
- [ ] Definir explicitamente a cobertura geográfica dos pacotes.
- [ ] Definir a alternativa de reserva, se necessária.
- [ ] Registrar a divisão de responsabilidades.

### Entrega da Etapa 1

- [x] Escolher o diferencial da equipe.
- [x] Documentar o problema e a solução proposta.
- [x] Descrever a integração com Hash, Árvore B e Grafo.
- [x] Submeter a proposta à professora.
- [x] Incorporar a descrição do diferencial ao README.
- [x] Integrar a documentação inicial à branch dev.
- [ ] Registrar o retorno da professora.
- [ ] Atualizar o documento caso a professora solicite alterações.

### Implementação futura

- [ ] Implementar o algoritmo de recomendação.
- [ ] Implementar o formulário de planejamento.
- [ ] Integrar a consulta de cobertura pela Hash.
- [ ] Integrar os dados dos clientes pela Árvore B.
- [ ] Integrar as rotas de menor latência pelo Grafo.
- [ ] Implementar os testes do diferencial.
- [ ] Atualizar a documentação final.

## 14. Observações

O diferencial foi escolhido pela equipe, mas sua implementação depende da aprovação.

As regras e os exemplos documentados representam o escopo técnico proposto e poderão ser ajustados durante a revisão, desde que as alterações sejam registradas e acordadas pela equipe.

A prioridade do projeto continuará sendo a implementação correta das estruturas de dados obrigatórias e sua integração com Flask.