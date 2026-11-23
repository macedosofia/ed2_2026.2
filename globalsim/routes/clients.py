
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


def package_service():
    return current_app.extensions["packages"]


def parse_client_form(form):
    raw_id = form.get("id", "").strip()
    raw_package = form.get("pacote", "").strip()

    try:
        client_id = int(raw_id)
    except ValueError:
        raise ValueError("O ID deve ser um inteiro positivo.")

    if client_id <= 0:
        raise ValueError("O ID deve ser um inteiro positivo.")

    package = None

    if raw_package:
        try:
            package = int(raw_package)
        except ValueError:
            raise ValueError("Código de pacote inválido.")

        if package <= 0:
            raise ValueError("Código de pacote inválido.")

        if package_service().find(package) is None:
            raise ValueError("O pacote selecionado não existe.")

    return {
        "id": client_id,
        "nome": form.get("nome", "").strip(),
        "email": form.get("email", "").strip(),
        "esim": form.get("esim", "").strip() or None,
        "pacote": package,
        "status": form.get("status", "").strip(),
    }


@blueprint.route("/clients/new", methods=["GET", "POST"])
def create():
    client = {
        "id": "",
        "nome": "",
        "email": "",
        "esim": "",
        "pacote": "",
        "status": "ativo",
    }

    status = 200

    if request.method == "POST":
        client = request.form.to_dict()

        try:
            record = parse_client_form(client)
            service().create(record)

        except ValueError as error:
            flash(str(error), "error")
            status = 400

        except OSError:
            flash(
                "Não foi possível salvar os dados. Tente novamente.",
                "error",
            )
            status = 503

        else:
            flash("Cliente cadastrado com sucesso.", "success")

            return redirect(
                url_for("clients.detail", client_id=record["id"]),
                code=303,
            )

    return render_template(
        "client_form.html",
        client=client,
        packages=package_service().list_all(),
        editing=False,
    ), status


@blueprint.route(
    "/clients/<int:client_id>/edit",
    methods=["GET", "POST"],
)
def edit(client_id):
    try:
        client = service().find(client_id)

    except ValueError as error:
        return render_template(
            "error.html",
            message=str(error),
        ), 400

    if client is None:
        return render_template(
            "error.html",
            message="Cliente não encontrado.",
        ), 404

    status = 200

    if request.method == "POST":
        client = request.form.to_dict()

        try:
            record = parse_client_form(client)

            if record["id"] != client_id:
                raise ValueError(
                    "O ID do cliente não pode ser alterado."
                )

            service().update(client_id, record)

        except ValueError as error:
            flash(str(error), "error")
            status = 400

        except LookupError:
            return render_template(
                "error.html",
                message="Cliente não encontrado.",
            ), 404

        except OSError:
            flash(
                "Não foi possível salvar os dados. Tente novamente.",
                "error",
            )
            status = 503

        else:
            flash(
                "Cliente atualizado com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "clients.detail",
                    client_id=client_id,
                ),
                code=303,
            )

        client["id"] = client_id

    return render_template(
        "client_form.html",
        client=client,
        packages=package_service().list_all(),
        editing=True,
    ), status
