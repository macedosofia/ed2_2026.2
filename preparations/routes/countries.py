from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from models.country import FIELDS

blueprint = Blueprint("countries", __name__)


def service():
    return current_app.extensions["countries"]


@blueprint.get("/")
def index():
    return render_template("index.html")


@blueprint.get("/countries")
def country_list():
    return render_template("countries.html", countries=service().list_all())


@blueprint.route("/countries/new", methods=["GET", "POST"])
def create():
    country = {}
    status = 200
    if request.method == "POST":
        country = request.form.to_dict()
        try:
            service().create(country)
        except ValueError as error:
            flash(str(error), "error")
            status = 400
        except OSError:
            flash("Não foi possível salvar os dados. Tente novamente.", "error")
            status = 503
        else:
            flash("País cadastrado com sucesso.", "success")
            return redirect(url_for("countries.country_list"), code=303)
    return render_template("country_form.html", country=country, fields=FIELDS, editing=False), status


@blueprint.get("/coverage")
def coverage():
    code = request.args.get("codigo", "")
    country = None
    searched = "codigo" in request.args
    status = 200
    if searched:
        try:
            country = service().find(code)
        except ValueError as error:
            flash(str(error), "error")
            status = 400
    return render_template("coverage.html", country=country, code=code, searched=searched and status == 200), status


@blueprint.route("/countries/<code>/edit", methods=["GET", "POST"])
def edit(code):
    try:
        country = service().find(code)
    except ValueError as error:
        return render_template("error.html", message=str(error)), 400
    if country is None:
        return render_template("error.html", message="País não encontrado."), 404
    status = 200
    if request.method == "POST":
        country = request.form.to_dict()
        try:
            service().update(code, country)
        except ValueError as error:
            flash(str(error), "error")
            status = 400
        except LookupError as error:
            return render_template("error.html", message=str(error)), 404
        except OSError:
            flash("Não foi possível salvar os dados. Tente novamente.", "error")
            status = 503
        else:
            flash("País atualizado com sucesso.", "success")
            return redirect(url_for("countries.country_list"), code=303)
        country["codigo"] = code.strip().upper()
    return render_template("country_form.html", country=country, fields=FIELDS, editing=True), status


@blueprint.post("/countries/<code>/delete")
def delete(code):
    try:
        service().remove(code)
    except ValueError as error:
        return render_template("error.html", message=str(error)), 400
    except LookupError as error:
        return render_template("error.html", message=str(error)), 404
    except OSError:
        return render_template("error.html", message="Não foi possível salvar a remoção. Tente novamente."), 503
    flash("País removido com sucesso.", "success")
    return redirect(url_for("countries.country_list"), code=303)


@blueprint.get("/instrumentation")
def instrumentation():
    return render_template("instrumentation.html", stats=service().statistics())
