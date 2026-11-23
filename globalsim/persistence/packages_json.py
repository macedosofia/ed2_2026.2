import json
from pathlib import Path


def load(path):
    path = Path(path)

    records = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(records, list):
        raise ValueError(
            "O arquivo de pacotes deve conter uma lista JSON."
        )

    return records