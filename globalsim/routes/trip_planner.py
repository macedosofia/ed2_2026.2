from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request


def create_trip_planner_blueprint(planner):
    blueprint = Blueprint("trip_planner", __name__)

    @blueprint.route("/trip-planner", methods=["GET", "POST"])
    def plan_trip():
        if request.method == "GET":
            return render_template("trip_planner.html", form={})

        form = request.form
        destinations = form.get("destinations", "").strip()
        client_id = form.get("client_id", "").strip()
        try:
            result = planner.recommend(
                origin=form.get("origin", ""),
                destinations=destinations.split(",") if destinations else [],
                duration_days=_parse_integer(form.get("duration_days", ""), "A duração"),
                data_gb=_parse_consumption(form.get("data_gb", "")),
                client_id=_parse_integer(client_id, "O ID do cliente") if client_id else None,
            )
        except ValueError as error:
            return render_template("trip_planner.html", form=form, error=str(error)), 400

        return render_template("trip_planner.html", form=form, result=result)

    return blueprint


def _parse_integer(value, field):
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{field} deve ser um inteiro positivo.") from error


def _parse_consumption(value):
    try:
        return Decimal(value.strip().replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("O consumo deve ser informado como um número em GB.") from error
