# Base demonstrativa de clientes

A base `globalsim/data/clients.demo.json` fornece 1.000 clientes para demonstrar a carga, as buscas e a listagem ordenada pela Árvore B na Etapa 2.

## Como a base é gerada

Cada registro tem os campos `id`, `nome`, `email`, `esim`, `pacote` e `status`. Os IDs são inteiros sequenciais de 1 a 1.000 e os e-mails usam o domínio `example.test`. Os status são `ativo` ou `inativo`. A base inclui 200 clientes com eSIM e pacote nulos. Para os demais, o gerador alterna os códigos retornados por `PackageService.list_all()`.

O gerador reutiliza `validate_client()` e verifica IDs repetidos antes da gravação. Com a quantidade padrão, a semente `2026` e o mesmo catálogo, `random.Random(seed)` reproduz a ordem de inserção fora da sequência dos IDs. Isso permite observar divisões durante a carga sem mudar as chaves usadas para busca.

## Geração e proteção dos dados

Execute na raiz do repositório. O exemplo grava em um diretório temporário e imprime as métricas da carga.

```bash
demo_dir="$(mktemp -d)"
python -m scripts.generate_clients_demo --output "$demo_dir/clients.demo.json"
```

O caminho padrão é `globalsim/data/clients.demo.json`. `--count` aceita um inteiro positivo e `--seed` aceita um inteiro. Para atualizar explicitamente a base demonstrativa versionada, execute `python -m scripts.generate_clients_demo --replace`.

O gerador escreve o lote em um arquivo temporário e confirma a carga pelo `ClientService` antes de publicar o arquivo completo. A operação padrão recusa um destino ocupado, inclusive se outro processo o criar durante a geração. A opção `--replace` autoriza apenas destinos chamados `clients.demo.json`. Essa regra e a rejeição de links simbólicos protegem `clients.json`, `countries.json`, `packages.json` e as outras bases.

## Carga e instrumentação

Use a interface pública do serviço para observar a carga e registrar a diferença no contador de buscas.

```python
from globalsim.services.clients import ClientService

service = ClientService("globalsim/data/clients.demo.json")
print(service.statistics())
assert service.find(1) is not None
assert service.find(1001) is None
print(service.statistics())
```

| Métrica | Após a carga | Após as duas buscas |
|---|---:|---:|
| `size` | 1.000 | 1.000 |
| `height` | 5 | 5 |
| `node_count` | 315 | 315 |
| `splits` | 310 | 310 |
| `lookups` | 0 | 2 |

## Uso no Flask

Com as dependências instaladas, execute o trecho abaixo a partir da raiz. `CLIENTS_PATH` aponta para uma cópia temporária, permitindo cadastrar ou editar clientes durante a demonstração. Abra a tela em `http://127.0.0.1:5000/clients`.

```python
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from globalsim.app import create_app

with TemporaryDirectory() as directory:
    demo_path = Path(directory) / "clients.demo.json"
    copyfile("globalsim/data/clients.demo.json", demo_path)
    app = create_app({"CLIENTS_PATH": demo_path})
    app.run()
```

## Testes

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -q
```

As duas execuções passaram com 221 testes em Python 3.12, incluindo 15 da base demonstrativa. Os testes verificam geração byte a byte, pacotes do catálogo, validação, proteção contra sobrescrita, carga, buscas, listagem e a configuração do Flask.
