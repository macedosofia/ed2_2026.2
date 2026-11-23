from decimal import Decimal

from globalsim.models.client import normalize_id
from globalsim.models.country import normalize_code


class TripPlannerService:
    def __init__(self, country_service, package_service, client_service=None):
        self._countries = country_service
        self._packages = package_service
        self._clients = client_service

    def recommend(self, origin, destinations, duration_days, data_gb, client_id=None):
        """Validate a trip and return its coverage and package recommendation."""
        origin = _normalize_country_code(origin, "A origem")
        if not isinstance(destinations, (list, tuple)) or not destinations:
            raise ValueError("Informe pelo menos um destino em uma lista ordenada.")

        destination_codes = list(dict.fromkeys(
            _normalize_country_code(code, "Cada destino") for code in destinations
        ))
        if type(duration_days) is not int or duration_days <= 0:
            raise ValueError("A duração deve ser um inteiro positivo.")
        data_gb = _validate_data_gb(data_gb)
        if client_id is not None:
            client_id = normalize_id(client_id)

        coverage = []
        missing_codes = []
        for code in destination_codes:
            country = self._countries.find(code)
            coverage.append({
                "codigo": code,
                "pais": country.get("pais") if country is not None else None,
                "cobertura": country is not None,
            })
            if country is None:
                missing_codes.append(code)

        status, package, explanation = self._recommend_package(
            destination_codes, missing_codes, duration_days, data_gb
        )
        client_status, client, current_package = self._lookup_client(client_id)
        return {
            "origem": origin,
            "destinos": coverage,
            "duracao_dias": duration_days,
            "consumo_gb": data_gb,
            "destinos_sem_cobertura": missing_codes,
            "status": status,
            "pacote_recomendado": package,
            "justificativa": explanation,
            "cliente_id": client_id,
            "status_cliente": client_status,
            "cliente": client,
            "pacote_atual": current_package,
        }

    def _recommend_package(self, destination_codes, missing_codes, duration_days, data_gb):
        if missing_codes:
            destinations = ", ".join(missing_codes)
            return "sem_cobertura", None, f"Sem cobertura cadastrada em {destinations}."

        required_countries = set(destination_codes)
        eligible = (
            package for package in self._packages.list_all()
            if package["dados_gb"] >= data_gb
            and package["validade_dias"] >= duration_days
            and required_countries.issubset(package["paises"])
        )
        package = min(
            eligible,
            key=lambda item: (
                item["dados_gb"], item["validade_dias"] - duration_days, item["codigo"]
            ),
            default=None,
        )
        if package is None:
            return (
                "sem_pacote",
                None,
                "Nenhum pacote compatível com os destinos, o consumo e a duração da viagem.",
            )

        consumption = str(data_gb).replace(".", ",")
        explanation = (
            f"{package['nome']} cobre {', '.join(destination_codes)} e oferece "
            f"{package['dados_gb']} GB por {package['validade_dias']} dias. "
            f"A viagem prevê {consumption} GB em {duration_days} dias. "
            "Entre os elegíveis, a seleção prioriza a menor franquia suficiente, "
            "a menor validade excedente e, por fim, o menor código."
        )
        return "recomendado", package, explanation

    def _lookup_client(self, client_id):
        if client_id is None:
            return "nao_informado", None, None
        if self._clients is None:
            return "consulta_indisponivel", None, None

        record = self._clients.find(client_id)
        if record is None:
            return "nao_encontrado", None, None

        client = {key: record[key] for key in ("id", "nome", "esim", "pacote", "status")}
        package_code = client["pacote"]
        current_package = self._packages.find(package_code) if package_code is not None else None
        return "encontrado", client, current_package


def _normalize_country_code(code, field):
    message = f"{field} deve ser um código de duas letras de A a Z."
    if isinstance(code, str) and not code.strip().isascii():
        raise ValueError(message)
    try:
        return normalize_code(code)
    except ValueError as error:
        raise ValueError(message) from error


def _validate_data_gb(value):
    if type(value) in (int, float, Decimal):
        amount = Decimal(str(value)) if type(value) is float else Decimal(value)
        if amount.is_finite() and amount > 0:
            return amount

    raise ValueError("O consumo deve ser um número positivo e finito.")
