# GlobalSIM — Estruturas de Dados II

Projeto desenvolvido para a disciplina de Estruturas de Dados II, com o objetivo de aplicar e integrar estruturas de dados em uma aplicação Web utilizando Python e Flask.

O GlobalSIM simula uma empresa de serviços internacionais de Internet móvel por eSIM, permitindo administrar países atendidos, clientes, pacotes de dados e uma rede internacional de conectividade.

O desenvolvimento está dividido em três etapas:

| Etapa | Estrutura principal | Funcionalidades |
| 1 | Tabela Hash | Gerenciamento de países e consulta de cobertura |
| 2 | Árvore B | Gerenciamento de clientes, eSIMs e pacotes |
| 3 | Grafo | Rede internacional e cálculo de rotas de menor latência |

As etapas são incrementais, de modo que as funcionalidades anteriores serão preservadas e integradas às novas estruturas.

## 1. Etapa 1 — Tabela Hash e Aplicação Web

**Prazo de entrega:** 20/10/2026

A primeira etapa consiste no desenvolvimento de uma aplicação Web para gerenciar os países atendidos pelo GlobalSIM.

A aplicação utiliza uma Tabela Hash implementada pela equipe, com tratamento de colisões por encadeamento separado, persistência em JSON e instrumentação para observar o comportamento da estrutura.

### Funcionalidades implementadas

- Página inicial do GlobalSIM.
- Cadastro de países atendidos.
- Consulta de cobertura por código do país.
- Listagem dos países cadastrados.
- Alteração dos dados de países.
- Remoção de países.
- Validação dos dados informados.
- Persistência em arquivo JSON.
- Instrumentação da Tabela Hash.
- Tratamento de erros e mensagens ao usuário.

Cada país possui os seguintes campos:

| Campo | Descrição | Exemplo |
| `codigo` | Código internacional de duas letras | BR |
| `pais` | Nome do país | Brasil |
| `regiao` | Região geográfica | América do Sul |
| `operadora` | Operadora responsável | Operadora BR |
| `tecnologia` | Tecnologia de conexão | 5G |

O código do país é utilizado como chave da Tabela Hash e não pode ser alterado durante a edição.

---

## 2. Tecnologias utilizadas

- Python 3.10 ou superior.
- Flask.
- HTML.
- CSS.
- Templates Jinja.
- JSON para persistência.
- Unittest para testes automatizados.
- Git e GitHub para versionamento e colaboração.

As estruturas de dados principais são implementadas pela equipe, sem substituição por bibliotecas prontas.

---

## 3. Instalação e execução

### 3.1. Clonar o repositório

```bash
git clone https://github.com/macedosofia/ed2_2026.2.git
```

Acesse o diretório do projeto:

```bash
cd ed2_2026.2
```

A implementação modular da Etapa 1 está localizada na pasta `preparations`.

Para acessar a versão de desenvolvimento:

```bash
git switch dev
```

Entre na pasta da aplicação:

```bash
cd preparations
```

Os comandos seguintes devem ser executados dentro de `preparations`.

### 3.2. Criar o ambiente virtual

```bash
python3 -m venv .venv
```

Ative o ambiente:

```bash
source .venv/bin/activate
```

### 3.3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 3.4. Executar a aplicação

```bash
python app.py
```

Abra o navegador e acesse:

http://127.0.0.1:5000

Para interromper o servidor, pressione `Ctrl + C` no terminal.

### 3.5. Persistência

Os registros dos países são armazenados em:

```text
data/countries.json
```

A base inicial pode estar vazia. Nesse caso, os países poderão ser cadastrados pela interface.

Ao iniciar a aplicação, os registros persistidos são carregados para a Tabela Hash em memória.

As consultas são realizadas na Hash, e não diretamente no arquivo JSON.

As operações de cadastro, atualização e remoção são persistidas no arquivo.

Arquivos JSON inválidos interrompem a inicialização sem serem sobrescritos automaticamente.

---

## 4. Organização do projeto

A implementação da Etapa 1 utiliza uma arquitetura modular, com separação entre rotas, modelos, serviços, estruturas de dados, persistência e interface.

| Caminho | Responsabilidade |
| `app.py` | Fábrica Flask e inicialização da aplicação |
| `models/country.py` | Validação e normalização dos dados dos países |
| `structures/hash_table.py` | Implementação da Tabela Hash e instrumentação |
| `services/countries.py` | Operações na Hash e coordenação da persistência |
| `persistence/countries_json.py` | Leitura e gravação atômica dos arquivos JSON |
| `routes/countries.py` | Rotas Flask, requisições GET/POST e tratamento de erros |
| `templates/` | Templates HTML utilizando Jinja |
| `static/css/style.css` | Estilos da interface |
| `data/` | Arquivos de dados persistidos |
| `tests/` | Testes automatizados e roteiros de teste |
| `docs/` | Contratos, documentação e especificação do diferencial |

### 4.1. Separação de responsabilidades

O funcionamento geral da aplicação segue o fluxo:

```text
Usuário
   |
   v
Interface Web
   |
   v
Rotas Flask
   |
   v
CountryService
   |
   +-------------------+
   |                   |
   v                   v
Validações         Tabela Hash
                       |
                       v
                 Países em memória

Nas operações de escrita:
CountryService → Persistência JSON
```

As rotas Flask recebem as requisições HTTP e delegam as operações ao serviço.

O serviço coordena as validações, a utilização da Tabela Hash e a persistência.

Essa organização facilita os testes, a manutenção e a integração com as próximas etapas do projeto.

### 4.2. Padrão de nomenclatura

Os nomes de arquivos, pastas, classes e rotas estão em inglês.

Os campos persistidos seguem a nomenclatura do enunciado:

- `codigo`
- `pais`
- `regiao`
- `operadora`
- `tecnologia`

A interface apresentada ao usuário permanece em português.

---

## 5. Rotas da aplicação

| Método | URL | Operação |
| GET | `/` | Página inicial |
| GET | `/countries` | Listagem de países |
| GET | `/countries/new` | Formulário de cadastro |
| POST | `/countries/new` | Cadastro de país |
| GET | `/coverage?codigo=BR` | Consulta de cobertura |
| GET | `/countries/<code>/edit` | Formulário de edição |
| POST | `/countries/<code>/edit` | Atualização de país |
| POST | `/countries/<code>/delete` | Remoção de país |
| GET | `/instrumentation` | Instrumentação da Tabela Hash |

### 5.1. Métodos HTTP

O método GET é utilizado para consultas e apresentação de páginas.

O método POST é utilizado nas operações que modificam os dados da aplicação.

As operações de cadastro, atualização e remoção seguem o padrão Post/Redirect/Get (PRG).

Após uma alteração bem-sucedida, a aplicação retorna um redirecionamento HTTP 303 para a página de listagem.

Esse comportamento evita o reenvio acidental de formulários ao atualizar a página de destino.

### 5.2. Validações e tratamento de erros

A aplicação realiza validações no servidor para garantir a consistência dos dados.

Entre as verificações implementadas estão:

- Código do país com exatamente duas letras.
- Normalização do código para letras maiúsculas.
- Campos obrigatórios preenchidos.
- Rejeição de códigos duplicados.
- Tratamento de países inexistentes.
- Impedimento de alteração da chave durante a edição.
- Proteção contra falhas de persistência.

Os principais códigos de resposta HTTP utilizados são:

| Código | Significado | Aplicação |
| 200 | OK | Consultas e páginas carregadas corretamente |
| 303 | See Other | Redirecionamento após mutações bem-sucedidas |
| 400 | Bad Request | Dados inválidos ou código duplicado |
| 404 | Not Found | Tentativa de editar ou remover país inexistente |
| 405 | Method Not Allowed | Utilização de método HTTP não permitido |
| 503 | Service Unavailable | Falhas de persistência tratadas pela aplicação |

Uma consulta com código válido, mas sem país cadastrado, apresenta cobertura indisponível.

---

## 6. Tabela Hash

A estrutura principal da Etapa 1 é uma Tabela Hash implementada pela equipe.

### 6.1. Características

- Capacidade inicial e fixa de 17 baldes.
- Função Hash polinomial de base 31.
- Tratamento de colisões por encadeamento separado.
- Código do país utilizado como chave.
- Rejeição de chaves duplicadas.
- Inserção, busca, atualização e remoção.
- Listagem dos registros.
- Instrumentação para análise do comportamento.

Os registros dos países são representados por dicionários Python.

Os dicionários não substituem a estrutura principal de busca, que permanece sendo a Tabela Hash.

### 6.2. Função Hash

A função Hash calcula um índice a partir dos caracteres do código do país.

O cálculo utiliza um acumulador, multiplicação pela base 31 e operação de módulo pela capacidade da tabela.

O índice calculado determina o balde em que o registro será armazenado ou procurado.

### 6.3. Tratamento de colisões

Uma colisão ocorre quando chaves diferentes produzem o mesmo índice.

O projeto utiliza encadeamento separado, permitindo armazenar múltiplos registros no mesmo balde.

Por exemplo, utilizando a capacidade padrão de 17 baldes:

```text
IT → índice 1
DE → índice 1
```

Os dois registros são armazenados no mesmo balde:

```text
Índice 1 → [IT, DE]
```

As operações percorrem o balde calculado e identificam os registros por suas chaves.

A remoção de um registro não deve prejudicar outros registros armazenados no mesmo balde.

### 6.4. Complexidade

A busca, a atualização e a remoção utilizam o índice calculado pela função Hash.

O custo médio esperado dessas operações por chave é:

```text
O(1 + fator de carga)
```

Além do custo de processamento da chave.

Em condições favoráveis de distribuição, esse custo é próximo de O(1).

No pior caso, quando muitos registros são armazenados no mesmo balde, o custo pode chegar a O(n).

A listagem percorre todos os baldes.

A persistência de uma alteração percorre os registros para regravar o JSON. Portanto, o fluxo completo de escrita possui custo O(n), mesmo quando a operação na Hash apresenta custo médio próximo de O(1).

### 6.5. Instrumentação

A aplicação disponibiliza uma página de instrumentação:

```text
/instrumentation
```

As métricas incluem:

- Capacidade da tabela.
- Quantidade de registros.
- Fator de carga.
- Quantidade de colisões.
- Colisões durante a carga inicial.
- Colisões durante operações posteriores.
- Ocupação dos baldes.
- Último índice calculado.

O fator de carga é definido por:

```text
Fator de carga = quantidade de registros / quantidade de baldes
```

A instrumentação permite observar o comportamento da estrutura durante as operações.

---

## 7. Persistência e consistência

A aplicação utiliza arquivos JSON para preservar os dados entre execuções.

O funcionamento segue o fluxo:

```text
Arquivo JSON
     |
     v
Carga inicial
     |
     v
Tabela Hash em memória
     |
     v
Operações do sistema
     |
     v
Atualização da estrutura
     |
     v
Persistência JSON
```

A implementação utiliza gravação atômica para reduzir o risco de arquivos parcialmente escritos.

O serviço também possui mecanismos de recuperação do estado anterior quando ocorre uma falha durante uma operação de escrita.

O objetivo é evitar inconsistências entre os registros em memória e os dados persistidos.

### Limitações da implementação

A aplicação foi organizada para execução local em um único processo.

O bloqueio utilizado pelo serviço sincroniza threads dentro desse processo.

Múltiplos processos independentes não compartilham automaticamente a mesma Tabela Hash.

Opcionalmente, a variável de ambiente `SECRET_KEY` poderá ser configurada para manter uma chave de sessão estável entre reinicializações.

---

## 8. Testes

O projeto utiliza `unittest` para verificar o funcionamento das estruturas e da aplicação Web.

### 8.1. Executar os testes

Dentro da pasta `preparations`, com o ambiente virtual ativado:

```bash
python -m unittest discover -s tests -v
```

Também é possível executar utilizando diretamente o interpretador do ambiente virtual:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

### 8.2. Cobertura dos testes

Os testes automatizados verificam:

- Colisões na Tabela Hash.
- Atualização e remoção de registros.
- Tratamento de JSON corrompido.
- Rejeição de tecnologia ausente.
- Rejeição de tecnologia em branco.
- Preenchimento do formulário de edição.
- Fluxo Post/Redirect/Get.
- Ciclo completo de cadastro, consulta, edição e remoção.
- Persistência após reinicialização.
- Códigos inválidos e inexistentes.
- Imutabilidade do código do país.
- Consultas utilizando a Hash em vez do JSON.
- Comportamento diante de falhas de gravação.

### 8.3. Resultado da validação

Na última execução informada durante o desenvolvimento da Etapa 1, foram executados 10 testes automatizados.

Resultado:

```text
Ran 10 tests in 0.090s

OK
```

Também foram realizados testes manuais pela interface Web, contemplando cadastro, consulta, edição, remoção, tratamento de duplicatas e persistência após reinicialização.

Esses resultados confirmam o funcionamento dos cenários testados, sem representar garantia de ausência de todos os possíveis defeitos.

---

## 9. Diferencial — Planejador Multidestinos com Recomendação Automática de Pacotes eSIM

**Status:** Escolhido pela equipe — aguardando aprovação da professora.

A equipe escolheu como diferencial o desenvolvimento de um Planejador Multidestinos com Recomendação Automática de Pacotes eSIM.

A proposta tem como objetivo auxiliar viajantes internacionais na escolha de pacotes de Internet compatíveis com seus roteiros.

### 9.1. Problema

Viajantes que visitam múltiplos países precisam considerar diferentes fatores ao escolher um pacote eSIM:

- Cobertura nos países de destino.
- Consumo estimado de dados.
- Duração da viagem.
- Franquia disponível.
- Validade dos pacotes.

A consulta individual de cobertura não permite identificar automaticamente qual pacote atende às necessidades de todo o roteiro.

O diferencial busca oferecer uma recomendação baseada em critérios objetivos, aproveitando as estruturas de dados desenvolvidas no projeto.

### 9.2. Funcionamento previsto

O usuário informará:

- País de origem.
- Países de destino.
- Duração total da viagem.
- Consumo estimado de Internet.

O sistema verificará a cobertura dos destinos e analisará os pacotes disponíveis.

Para ser considerado elegível, um pacote deverá:

1. Oferecer cobertura em todos os países do roteiro.
2. Possuir franquia suficiente para o consumo estimado.
3. Possuir validade igual ou superior à duração da viagem.

Entre os pacotes elegíveis, propõe-se recomendar aquele que apresentar a menor franquia suficiente.

Em caso de empate, será considerada a menor validade excedente e, persistindo o empate, o menor código identificador.

Os critérios definitivos serão confirmados pela equipe antes da implementação.

Caso nenhum pacote seja compatível, o sistema informará que não existe uma recomendação adequada.

### 9.3. Exemplo de utilização

Considere a seguinte viagem:

```text
Origem: Brasil

Destinos:
- Portugal
- França
- Itália

Duração: 25 dias

Consumo estimado: 8 GB
```

O sistema verificará a cobertura em cada destino utilizando a Tabela Hash.

Em seguida, analisará os pacotes cadastrados.

Considerando, para fins de exemplo, que Europa Basic, Europa Plus e Global cobrem os três destinos:

| Pacote | Dados | Validade | Elegível |
| Europa Basic | 5 GB | 15 dias | Não |
| Europa Plus | 10 GB | 30 dias | Sim |
| Global | 20 GB | 30 dias | Sim |

O pacote recomendado será:

**Europa Plus — 10 GB por 30 dias.**

A escolha ocorre porque o pacote cobre todos os destinos, oferece dados suficientes e possui validade adequada.

Entre os pacotes elegíveis do exemplo, apresenta a menor franquia suficiente.

A cobertura geográfica utilizada nesse exemplo é ilustrativa e deverá ser definida explicitamente pela equipe.

### 9.4. Integração com as estruturas

O diferencial será desenvolvido de forma incremental.

| Estrutura | Utilização no planejador |
| Tabela Hash | Verificar a cobertura de cada destino |
| Árvore B | Recuperar os dados do cliente e seu pacote atual |
| Grafo | Calcular rotas de menor latência entre os destinos |
| Algoritmo de recomendação | Filtrar e selecionar um pacote compatível |

**Etapa 1 — Tabela Hash**

Será documentada a proposta e sua integração com a consulta de cobertura dos países.

**Etapa 2 — Árvore B**

Será desenvolvido o núcleo funcional do planejador, incluindo a recomendação de pacotes e a integração com os registros de clientes.

**Etapa 3 — Grafo**

Será acrescentada a análise de conectividade entre os destinos, utilizando Dijkstra para calcular os caminhos de menor latência na rede simulada.

A ordem de visitação dos países será definida pelo usuário. O sistema calculará as rotas de conectividade para os trechos informados, sem otimizar a ordem da viagem.

### 9.5. Escopo e limitações

Para manter o projeto viável, a primeira versão do diferencial terá as seguintes limitações:

- Recomendação de apenas um pacote para toda a viagem.
- Sem combinação de múltiplos pacotes.
- Sem pagamento ou compra de pacotes.
- Sem consulta a operadoras reais.
- Sem necessidade de autenticação com Google.
- Sem dependência de LLMs ou APIs externas.
- Recomendação baseada em regras determinísticas.
- Utilização de latências simuladas no Grafo.

A equipe poderá avaliar melhorias adicionais depois de concluir os requisitos obrigatórios.

### 9.6. Documentação detalhada

A especificação completa do diferencial está disponível em:

[docs/differential.md](docs/differential.md)

O documento apresenta o problema, o funcionamento proposto, os critérios de recomendação, a integração com as estruturas de dados e os cenários previstos para validação.

---

## 10. Próximas etapas

### Etapa 2 — Árvore B e Gerenciamento de Clientes

**Prazo:** 24/11/2026

A segunda etapa ampliará o GlobalSIM para administrar clientes, eSIMs e pacotes.

As principais funcionalidades previstas incluem:

- Implementação própria da Árvore B.
- Inserção de clientes.
- Busca por identificador.
- Listagem e atualização de registros.
- Carga de aproximadamente 1.000 clientes.
- Associação de eSIM e pacote ao cliente.
- Persistência dos registros.
- Integração com a Tabela Hash.
- Instrumentação da Árvore B.
- Primeira implementação funcional do diferencial, quando aplicável.

As funcionalidades da Etapa 1 deverão continuar funcionando.

### Etapa 3 — Grafo e Integração Final

**Prazo:** 01/12/2026

A terceira etapa incluirá a representação da rede internacional utilizando um Grafo ponderado.

Estão previstos:

- Implementação do Grafo.
- Busca em Largura (BFS).
- Busca em Profundidade (DFS).
- Algoritmo de Dijkstra.
- Cálculo de caminhos de menor latência.
- Visualização da rede.
- Consulta integrada entre cliente, pacote, cobertura e conectividade.
- Integração final do diferencial.
- Documentação e apresentação do sistema.

---

## 11. Colaboração e versionamento

O projeto é desenvolvido colaborativamente utilizando Git e GitHub.

O fluxo de trabalho adotado utiliza:

- `main`: versões estáveis destinadas à entrega.
- `dev`: integração das funcionalidades em desenvolvimento.
- Branches específicas para funcionalidades, correções, testes e documentação.

As alterações são realizadas preferencialmente em branches próprias e integradas por Pull Requests.

Antes da integração, recomenda-se:

1. Revisar as alterações realizadas.
2. Executar os testes relacionados.
3. Executar os testes de regressão.
4. Realizar commits pequenos e descritivos.
5. Solicitar a revisão de outro integrante.
6. Integrar as alterações à `dev`.

Para as entregas, a equipe poderá utilizar tags como:

```text
etapa-1
etapa-2
etapa-3
```

---

## 12. Pendências da Etapa 1

Antes da entrega final, a equipe deverá verificar:

- [x] Implementação da Tabela Hash.
- [x] Cadastro de países.
- [x] Consulta de cobertura.
- [x] Listagem dos países.
- [x] Edição e remoção.
- [x] Persistência JSON.
- [x] Instrumentação da Hash.
- [x] Testes automatizados das funcionalidades principais.
- [x] Testes manuais das operações Web.
- [x] Escolha do diferencial pela equipe.
- [x] Documentação inicial do diferencial.
- [ ] Confirmar os critérios definitivos de recomendação.
- [ ] Definir a cobertura geográfica dos pacotes para as próximas etapas.
- [ ] Submeter o diferencial à professora.
- [ ] Registrar o retorno da professora.
- [ ] Preparar ou confirmar os dados de demonstração.
- [ ] Revisar a documentação com a equipe.
- [ ] Executar os testes finais na versão integrada.
- [ ] Preparar a versão de entrega da Etapa 1.

O desenvolvimento das próximas etapas deverá preservar a implementação da Tabela Hash e manter a separação entre estruturas de dados, regras da aplicação e interface Web.