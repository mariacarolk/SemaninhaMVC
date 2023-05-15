from datetime import date
from flask import Blueprint
from flask import render_template, url_for, flash, redirect
from Semaninha_MVC.controllers.forms import PedidoForm, NewPedidoProdutoForm, DeleteButton, PedidoClienteForm
from Semaninha_MVC.controllers import general_controller
from Semaninha_MVC.models import cliente_model, pedido_model, produto_final_model, utils, cardapio_model

# create a blueprint for the cardapio routes
pedido_bp = Blueprint('pedido_bp', __name__)

@pedido_bp.route("/novo_pedido", methods=["GET", "POST"])
def novo_pedido():
    conn = utils.get_db()
    form = PedidoForm()

    # Busca os clientes para opção
    clientes = [(str(cliente[0]), cliente[1]) for cliente in cliente_model.busca_todos_clientes(conn)]
    form.cliente.choices = clientes

    # Busca os status de pagamento
    form.status_pagamento.choices = general_controller.busca_status("Pagamento", conn)

    # Busca os status de entrega
    form.status_entrega.choices = general_controller.busca_status("Entrega", conn)

    if form.validate_on_submit():
        # Process the form data
        pedido_model.insert(form, conn)

        # Redirect to some page
        flash("Pedido inserido com sucesso", "success")
        return redirect(url_for("index"))

    return render_template("pedido/novo_pedido.html", form=form)

@pedido_bp.route("/pedidos")
def pedidos():
    conn = utils.get_db()
    pedidos_db = pedido_model.busca_todos_pedidos(conn)
    pedidos = []

    for row in pedidos_db:
        pedido = {
            "id"               : row[0],
            "cliente"          : row[1],
            "data_pedido"      : row[2],
            "data_entrega"     : row[3],
            "valor"            : row[4],
            "status_pagamento" : utils.busca_status_por_id(row[5], conn),
            "status_entrega"   : utils.busca_status_por_id(row[6], conn)
        }
        pedidos.append(pedido)

    return render_template("pedido/pedidos.html", pedidos=pedidos)

@pedido_bp.route("/pedido/<int:id_pedido>")
def pedido(id_pedido):
    conn = utils.get_db()
    # busca os dados do pedido
    pedido_from_db = pedido_model.busca_dados_pedido(id_pedido, conn)

    try:
        pedido = {
            "id": pedido_from_db[0],
            "id_cliente": pedido_from_db[1],
            "nome": pedido_from_db[2],
            "data_pedido": pedido_from_db[3],
            "data_entrega": pedido_from_db[4],
            "valor": pedido_from_db[5],
            "status_pagamento": utils.busca_status_por_id(pedido_from_db[6], conn),
            "status_entrega": utils.busca_status_por_id(pedido_from_db[7], conn),
            "observacoes": pedido_from_db[8]
        }
    except:
        pedido = {}

    if pedido:
        # busca os produtos que compôem o pedido
        pedido_produto_from_db = pedido_model.busca_pedido_produto(id_pedido, conn)
        pedido_produto = []

        for row in pedido_produto_from_db:
            row = {
                "id_pedido"  : row[0],
                "id_produto" : row[1],
                "produto"    : row[2],
                "qtd_produto": row[3]

            }
            pedido_produto.append(row)

        pedidoProdutoForm = NewPedidoProdutoForm()
        pedidoProdutoForm.id_pedido.data = id_pedido

        produtos = [(str(produto[0]), produto[1]) for produto in produto_final_model.busca_todos_produtos(conn)]
        pedidoProdutoForm.produto.choices = produtos

        deletePedido = DeleteButton()
        deletePedidoProduto = DeleteButton()

        return render_template("pedido/pedido.html",
                               pedidoProdutoForm=pedidoProdutoForm,
                               pedido=pedido,
                               pedido_produto=pedido_produto,
                               deletePedido=deletePedido,
                               deletePedidoProduto=deletePedidoProduto)
    return redirect(url_for("index"))

@pedido_bp.route("/pedidoproduto/new", methods=["POST"])
def new_pedido_produto():
    conn = utils.get_db()
    form = NewPedidoProdutoForm()

    produtos = [(str(produto[0]), produto[1]) for produto in produto_final_model.busca_todos_produtos(conn)]
    form.produto.choices = produtos

    if form.validate_on_submit():
        pedido_model.insert_pedido_produto(form, conn)

    return redirect(url_for('pedido_bp.pedido', id_pedido=form.id_pedido.data))

@pedido_bp.route("/delete_pedido/<int:id_pedido>/<id_cliente>/delete", methods=["POST"])
def delete_pedido(id_pedido, id_cliente):
    conn = utils.get_db()
    pedido_model.delete_pedido(id_pedido, conn)

    flash("Pedido deletado com sucesso.")

    if id_cliente == 'None':
        return redirect(url_for('pedido_bp.pedidos'))
    else:
        return redirect(url_for('cliente_bp.cliente', id_cliente=id_cliente))

@pedido_bp.route("/pedidoproduto/<int:id_pedido>/<int:id_produto>/delete", methods=["POST"])
def delete_pedido_produto(id_pedido, id_produto):
    conn = utils.get_db()
    pedido_model.delete_pedido_produto(id_pedido, id_produto, conn)

    flash("Produto deletado com sucesso.")

    return redirect(url_for('pedido_bp.pedido', id_pedido=id_pedido))

@pedido_bp.route("/novo_pedido_cliente", methods=["GET", "POST"])
def novo_pedido_cliente():
    conn = utils.get_db()
    form = PedidoClienteForm()
    form.data_entrega.choices = cardapio_model.busca_datas_entrega(date=date.today(), conn=conn)

    # Busca os produtos que estão disponíveis no cardápio no dia atual
    produtos_cardapio_from_db = cardapio_model.busca_produtos_cardapio(date=date.today(), conn=conn)

    produtos = []

    for row in produtos_cardapio_from_db:
        produto = {
            "id": row[0],
            "produto": row[1],
            "qtd_produto": row[2],
            "preco_venda": row[3],
            "descricao": row[4]
        }

        produtos.append(produto)

    if form.validate_on_submit():
        flash("Pedido inserido com sucesso", "success")
        return redirect(url_for("pedido_bp.novo_pedido"))

    return render_template("pedido/novo_pedido_cliente.html", form=form, produtos=produtos)

