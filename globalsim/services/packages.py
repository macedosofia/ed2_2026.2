from copy import deepcopy
from pathlib import Path

from globalsim.models.package import validate_package
from globalsim.persistence import packages_json


class PackageService:
    def __init__(self, path=None):
        if path is None:
            path = (
                Path(__file__).resolve().parents[1]
                / "data"
                / "packages.json"
            )

        self._packages = {}

        for record in packages_json.load(path):
            package = validate_package(record)
            codigo = package["codigo"]

            if codigo in self._packages:
                raise ValueError(
                    f"Já existe um pacote com o código {codigo}."
                )

            self._packages[codigo] = package

    def find(self, codigo):
        if type(codigo) is not int or codigo <= 0:
            raise ValueError(
                "O código do pacote deve ser um inteiro positivo."
            )

        package = self._packages.get(codigo)

        if package is None:
            return None

        return deepcopy(package)

    def list_all(self):
        return [
            deepcopy(self._packages[codigo])
            for codigo in sorted(self._packages)
        ]