import re

FIELDS = {"codigo": "Código", "pais": "País", "regiao": "Região", "operadora": "Operadora", "tecnologia": "Tecnologia"}


def normalize_code(value):
    if not isinstance(value, str):
        raise ValueError("Informe um código com duas letras.")
    code = value.strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", code):
        raise ValueError("O código deve conter duas letras de A a Z.")
    return code


def validate_country(record):
    if not isinstance(record, dict):
        raise ValueError("Registro de país inválido.")
    country = {}
    for field, label in FIELDS.items():
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo {label} é obrigatório.")
        country[field] = value.strip()
    country["codigo"] = normalize_code(country["codigo"])
    return country
