
import re


def normalize_id(client_id):
    if type(client_id) is not int or client_id <= 0:
        raise ValueError("O ID deve ser um inteiro positivo.")

    return client_id


def validate_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"O campo {field} deve ser um texto válido.")

    return value.strip()


def validate_client(record):
    if not isinstance(record, dict):
        raise ValueError("O cliente deve ser um dicionário.")

    client_id = normalize_id(record.get("id"))
    nome = validate_text(record.get("nome"), "nome")
    email = validate_text(record.get("email"), "email")
    status = validate_text(record.get("status"), "status")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("E-mail inválido.")

    esim = record.get("esim")

    if esim is not None:
        esim = validate_text(esim, "esim")

    pacote = record.get("pacote")

    if pacote is not None:
        if type(pacote) is not int or pacote <= 0:
            raise ValueError("O pacote deve ser um inteiro positivo.")

    return {
        "id": client_id,
        "nome": nome,
        "email": email,
        "esim": esim,
        "pacote": pacote,
        "status": status
    }
