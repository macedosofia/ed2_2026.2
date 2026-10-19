import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from tabela_hash import TabelaHash

app = Flask(__name__)
app.secret_key = "troque-isso"

tabela = TabelaHash(tamanho=11)

ARQUIVO = os.path.join(app.root_path, "paises.json")


def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, encoding="utf-8") as f:
            for item in json.load(f):
                tabela.inserir(item["codigo"], {"nome": item["nome"]})


def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump([{"codigo": c, **d} for c, d in tabela.listar()],
                  f, ensure_ascii=False, indent=2)


carregar()


@app.route("/")
def index():
    return render_template(
        "index.html",
        itens=tabela.listar(),
        fator=tabela.fator_de_carga(),
        colisoes=tabela.colisoes,
        quantidade=tabela.quantidade,
    )


@app.route("/inserir", methods=["POST"])
def inserir():
    codigo = request.form["codigo"].strip()
    nome = request.form["nome"].strip()
    if not codigo or not nome:
        flash("Preencha código e nome")
        return redirect(url_for("index"))
    try:
        tabela.inserir(codigo, {"nome": nome})
        salvar()
        flash("Inserido com sucesso!")
    except KeyError as e:
        flash(e.args[0])
    return redirect(url_for("index"))


@app.route("/buscar")
def buscar():
    codigo = request.args.get("codigo", "")
    dados = tabela.buscar(codigo)
    if dados is None:
        return jsonify({"encontrado": False}), 404
    return jsonify({"encontrado": True, "codigo": codigo.strip().upper(), "dados": dados})


@app.route("/atualizar", methods=["POST"])
def atualizar():
    codigo = request.form["codigo"]
    nome = request.form["nome"]
    if tabela.atualizar(codigo, {"nome": nome}):
        flash("Atualizado!")
    else:
        flash("Código não encontrado")
    return redirect(url_for("index"))


@app.route("/remover/<codigo>", methods=["POST"])
def remover(codigo):
    if tabela.remover(codigo):
        flash("Removido!")
    else:
        flash("Código não encontrado")
    return redirect(url_for("index"))


@app.route("/ocupacao")
def ocupacao():
    return render_template("ocupacao.html", baldes=tabela.ocupacao())


if __name__ == "__main__":
    app.run(debug=True)