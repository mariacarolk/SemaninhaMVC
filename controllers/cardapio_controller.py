from flask import Blueprint, flash, redirect, render_template, url_for, request, jsonify
from Semaninha_MVC.controllers import forms
from Semaninha_MVC.models import cardapio_model, utils

# create a blueprint for the cardapio routes
cardapio_bp = Blueprint('cardapio_bp', __name__)


def busca_cardapios(conn):
    cardapios_db = cardapio_model.busca_todos_cardapios(conn)

    cardapios = []

    for row in cardapios_db:
        cardapio = {
            "id": row[0],
            "data_inicio": row[1],
            "data_fim": row[2]
        }
        cardapios.append(cardapio)

    return cardapios

def busca_dados_cardapio(id, conn):
    cardapio_db, produtos_db = cardapio_model.busca_dados_cardapio_completo(id, conn)

    cardapio = {
        "id": cardapio_db[0],
        "data_inicio": cardapio_db[1],
        "data_fim": cardapio_db[2]
    }
    produtos = []

    for row in produtos_db:
        produto = {
            "id_produto": row[0],
            "produto": row[1],
            "observacoes": row[2]
        }
        produtos.append(produto)

    return cardapio, produtos

@cardapio_bp.route("/novo_cardapio", methods=["GET", "POST"])
def novo_cardapio():
    conn = utils.get_db()
    form = forms.CardapioPeriodoForm()

    # Busca os produtos
    for i in range(len(form.produtos)):
        form.produtos[i].produto.choices = utils.busca_produtos(conn)

    if request.method == 'POST' and 'add_row' in request.form:
        form.produtos.append_entry()

    if form.validate_on_submit():
        # Process the form data
        last_id = cardapio_model.insert(form, conn)

        # faz um for para inserir todos os produtos para o cardápio
        for produto_form in form.produtos:
            cardapio_model.insert_cardapio_produto(last_id,
                                                   produto_form.produto.data,
                                                   produto_form.imagem.data,
                                                   produto_form.observacoes.data,
                                                   conn)

        # Redirect to some page
        flash("Cardápio inserido com sucesso", "success")
        return redirect(url_for("cardapio_bp.novo_cardapio"))

    if request.method == 'POST' and 'add_row' in request.form:
        return jsonify(result="success", message="Row added successfully")  # Return success response for AJAX request

    form = forms.CardapioPeriodoForm()
    # Busca os produtos
    for i in range(len(form.produtos)):
        form.produtos[i].produto.choices = utils.busca_produtos(conn)
    # Busca dados dos cardápios já cadastrados
    cardapios = busca_cardapios(conn)
    deleteCardapio = forms.DeleteButton()

    return render_template("cardapio/novo_cardapio.html",
                           form=form,
                           cardapios=cardapios,
                           deleteCardapio=deleteCardapio)


@cardapio_bp.route("/delete_cardapio/<int:id>", methods=["POST"])
def delete_cardapio(id):
    conn = utils.get_db()

    try:
        # Attempt to delete the row with the specified id
        cardapio_model.delete_cardapio(id, conn)
        flash('Cardápio deletado com sucesso')
    except utils.DeleteError as e:
        flash(str(e))

    form = forms.CardapioPeriodoForm()
    # Busca os produtos
    form.produtos[0].produto.choices = utils.busca_produtos(conn)
    # Busca dados dos cardápios já cadastrados
    cardapios = busca_cardapios(conn)
    deleteCardapio = forms.DeleteButton()

    return render_template("cardapio/novo_cardapio.html",
                            form=form,
                            cardapios=cardapios,
                            deleteCardapio=deleteCardapio)

@cardapio_bp.route("/delete_cardapio_produto/<int:id_cardapio>/<int:id_produto>/delete", methods=["POST"])
def delete_cardapio_produto(id_cardapio, id_produto):
    conn = utils.get_db()
    cardapio_model.delete_cardapio_produto(id_cardapio, id_produto, conn)

    flash("Produto deletado com sucesso.")

    return redirect(url_for('cardapio_bp.cardapio', id=id_cardapio))


@cardapio_bp.route("/cardapio/<int:id>")
def cardapio(id):
    conn = utils.get_db()
    cardapio, produtos = busca_dados_cardapio(id, conn)

    deleteCardapio = forms.DeleteButton()
    deleteCardapioProduto = forms.DeleteButton()

    return render_template("cardapio/cardapio.html",
                           cardapio=cardapio,
                           produtos=produtos,
                           deleteCardapio=deleteCardapio,
                           deleteCardapioProduto=deleteCardapioProduto)