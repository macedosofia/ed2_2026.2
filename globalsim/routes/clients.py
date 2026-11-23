
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)


blueprint = Blueprint("clients", __name__)


def service():
    return current_app.extensions["clients"]


@blueprint.get("/clients")
def client_list():
    clients = service().list_all()
    return render_template("clients.html", clients=clients)


@blueprint.get("/clients/search")
def search():
    raw_id = request.args.get("id", "").strip()

    try:
        client_id = int(raw_id)
        client = service().find(client_id)
    except ValueError:
        flash("O ID deve ser um inteiro positivo.", "error")
        return render_template(
            "clients.html",
            clients=[],
            search_id=raw_id,
        ), 400

    if client is None:
        flash("Cliente não encontrado.", "error")
        return render_template(
            "clients.html",
            clients=[],
            search_id=raw_id,
        ), 404

    return redirect(
        url_for("clients.detail", client_id=client_id)
    )


@blueprint.get("/clients/<int:client_id>")
def detail(client_id):
    try:
        client = service().find(client_id)
    except ValueError:
        return render_template(
            "error.html",
            message="O ID deve ser um inteiro positivo.",
        ), 400

    if client is None:
        return render_template(
            "error.html",
            message="Cliente não encontrado.",
        ), 404

    return render_template(
        "client_detail.html",
        client=client,
    )
