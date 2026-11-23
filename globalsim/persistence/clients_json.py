
import json
import os
import tempfile
from pathlib import Path


def load(path):
    path = Path(path)

    if not path.exists():
        return []

    records = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(records, list):
        raise ValueError("O JSON de clientes deve conter uma lista.")

    return records


def save(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)

            json.dump(
                records,
                temporary,
                ensure_ascii=False,
                indent=2
            )

            temporary.write("\n")

        os.replace(temporary_path, path)

    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
