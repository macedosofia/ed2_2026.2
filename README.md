# GlobalSIM — Estruturas de Dados II

Aplicação Flask da entrega 1 (20/10/2026), com página inicial, cadastro, consulta de cobertura, listagem, edição e remoção de países. As operações usam uma Tabela Hash própria, com persistência em JSON e instrumentação visível.

## Executar

Python 3.10 ou superior. Na raiz do projeto:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000. A base `data/countries.json` começa vazia; cadastre países pela interface. A aplicação carrega os registros na Hash ao iniciar. Arquivos inválidos interrompem a inicialização sem serem sobrescritos.

## Testar

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Os testes implementados cobrem o fluxo HTTP, reinício, colisões, duplicatas, códigos inválidos/inexistentes, chave imutável, remoção por POST e falhas de gravação. Os demais arquivos de teste ainda contêm roteiros para expansão.

## Organização

| Caminho | Responsabilidade |
|---|---|
| `app.py` | Fábrica Flask e inicialização |
| `models/country.py` | Validação e normalização |
| `structures/hash_table.py` | Hash com encadeamento separado e instrumentação |
| `services/countries.py` | Operações na Hash e coordenação da persistência |
| `persistence/countries_json.py` | Leitura e gravação atômica JSON |
| `routes/countries.py` | Rotas GET/POST, validações e mensagens |
| `templates/` | Páginas Jinja em português |
| `static/css/style.css` | Estilos da interface |
| `data/` | Dados persistidos e roteiro de preparação |
| `tests/` | Testes e roteiros de testes |
| `docs/` | Contratos, checklist e proposta de diferencial |

Nomes de arquivos, pastas, classes e rotas estão em inglês. Os campos persistidos (`codigo`, `pais`, `regiao`, `operadora`, `tecnologia`) seguem o enunciado; a interface permanece em português.

## Rotas

| Método | URL | Operação |
|---|---|---|
| GET | `/` | Início |
| GET | `/countries` | Listagem |
| GET / POST | `/countries/new` | Formulário / cadastro |
| GET | `/coverage?codigo=BR` | Consulta pela Hash |
| GET / POST | `/countries/<code>/edit` | Formulário / alteração |
| POST | `/countries/<code>/delete` | Remoção |
| GET | `/instrumentation` | Métricas da Hash |

Mutações bem-sucedidas retornam redirecionamento 303. Entradas inválidas e duplicatas retornam 400; edição/remoção de país ausente, 404; falhas de persistência, 503, preservando o estado anterior. Consulta válida sem país cadastrado exibe cobertura indisponível. O código de um país não pode ser alterado na edição.

## Tabela Hash

A tabela usa 17 baldes, encadeamento por listas e hash polinomial de base 31 reduzido à capacidade. Dicionários representam somente registros. Busca, alteração e remoção percorrem o balde calculado; a listagem percorre todos os baldes. O custo médio esperado dessas operações por chave é O(1 + fator de carga), além do cálculo da chave; o pior caso é O(n). A capacidade é fixa.

A interface mostra ocupação, último índice, fator de carga e colisões separadas entre carga inicial e inserções posteriores. Colisão significa inserir com sucesso em balde ocupado; duplicatas recusadas não incrementam a contagem. Persistir uma mutação percorre todos os registros, portanto o fluxo completo de escrita é O(n).

A aplicação foi organizada para execução local em um único processo. O bloqueio do serviço sincroniza threads desse processo; múltiplos processos não compartilham a Hash. Opcionalmente, defina `SECRET_KEY` no ambiente para manter sessões entre reinícios.

# Próximos passos

Preencher o JSON com dados de demonstração [countries.json] está vazio. Recomenda-se incluir os oito países do enunciado: BR, PT, ES, FR, IT, US, CA e JP.


Definir o diferencial da equipe
[differential.md] contém apenas uma proposta. Precisamos escolher o diferencial, explicar sua integração futura e registrar se foi submetido/aprovado pela professora.
