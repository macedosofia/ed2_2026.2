from globalsim.models.country import normalize_code


def validate_package(record):
    if not isinstance(record, dict):
        raise ValueError("Registro de pacote inválido.")

    codigo = record.get("codigo")

    if type(codigo) is not int or codigo <= 0:
        raise ValueError("O código do pacote deve ser um inteiro positivo.")

    nome = record.get("nome")

    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("O nome do pacote é obrigatório.")

    dados_gb = record.get("dados_gb")

    if type(dados_gb) is not int or dados_gb <= 0:
        raise ValueError("A franquia de dados deve ser um inteiro positivo.")

    validade_dias = record.get("validade_dias")

    if type(validade_dias) is not int or validade_dias <= 0:
        raise ValueError("A validade deve ser um inteiro positivo.")

    paises = record.get("paises")

    if not isinstance(paises, list) or not paises:
        raise ValueError("O pacote deve atender pelo menos um país.")

    paises_normalizados = [
        normalize_code(pais) for pais in paises
    ]

    if len(paises_normalizados) != len(set(paises_normalizados)):
        raise ValueError("O pacote contém países duplicados.")

    return {
        "codigo": codigo,
        "nome": nome.strip(),
        "dados_gb": dados_gb,
        "validade_dias": validade_dias,
        "paises": paises_normalizados,
    }