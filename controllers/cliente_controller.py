from flask import Blueprint, render_template, request, url_for, flash, redirect
from Semaninha_MVC.controllers import forms
from Semaninha_MVC.models import cliente_model, utils

# create a blueprint for the client routes
cliente_bp = Blueprint('cliente_bp', __name__)


@cliente_bp.route("/novo_cliente", methods=["GET", "POST"])
def novo_cliente():
    conn = utils.get_db()
    form = forms.ClienteForm()

    if form.validate_on_submit():
        cliente_model.insert(form, conn)

        # Redirect to some page
        flash("Cliente {} inserido com sucesso".format(request.form.get("nome")), "success")
        return redirect(url_for("index"))

    return render_template("cliente/novo_cliente.html", form=form)


@cliente_bp.route("/clientes")
def clientes():
    conn = utils.get_db()
    clientes_db = cliente_model.busca_todos_clientes(conn)

    clientes = []

    for cliente in clientes_db:
        cliente = {
            "id": cliente[0],
            "nome": cliente[1],
            "endereco": cliente[2],
            "bairro": cliente[3],
            "cidade": cliente[4],
            "telefone": cliente[5],
            "restricoes": cliente[6],
            "observacoes": cliente[7]
        }
        clientes.append(cliente)

    return render_template("cliente/clientes.html", clientes=clientes)


@cliente_bp.route("/cliente/<int:id_cliente>")
def cliente(id_cliente):
    conn = utils.get_db()
    cliente_from_db = cliente_model.busca_dados_cliente(id_cliente, conn)

    cliente = {}
    if cliente_from_db:
        cliente = {
            "id": cliente_from_db[0],
            "nome": cliente_from_db[1],
            "endereco": cliente_from_db[2],
            "bairro": cliente_from_db[3],
            "cidade": cliente_from_db[4],
            "telefone": cliente_from_db[5],
            "restricoes": cliente_from_db[6],
            "observacoes": cliente_from_db[7]
        }

    if cliente:
        pedidos_from_db = cliente_model.busca_pedidos_cliente(id_cliente, conn)

        pedidos = []

        for row in pedidos_from_db:
            pedido = {
                "id": row[0],
                "data_pedido": row[1],
                "data_entrega": row[2],
                "valor": row[3],
                "status_pagamento": utils.busca_status_por_id(row[4], conn),
                "status_entrega": utils.busca_status_por_id(row[5], conn),
                "observacoes": row[6]
            }
            pedidos.append(pedido)

        deleteCliente = forms.DeleteButton()
        deletePedido = forms.DeleteButton()

        return render_template("cliente/cliente.html",
                               cliente=cliente,
                               pedidos=pedidos,
                               deleteCliente=deleteCliente,
                               deletePedido=deletePedido)

    return redirect(url_for("index"))

@cliente_bp.route("/deletecliente/<int:id_cliente>/delete", methods=["POST"])
def delete_cliente(id_cliente):
    conn = utils.get_db()
    cliente_model.delete_cliente(id_cliente, conn)

    flash("Cliente deletado com sucesso.")

    return redirect(url_for('cliente_bp.clientes'))
