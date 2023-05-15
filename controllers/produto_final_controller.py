from flask import Blueprint
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect
from Semaninha_MVC.controllers import forms
from Semaninha_MVC.models import produto_final_model, preparo_model, materia_prima_model, utils

# create a blueprint for the produto final routes
produto_final_bp = Blueprint('produto_final_bp', __name__)

def atualiza_custo_produto_preparo(id_preparo, conn):
    # Busca os produtos que utilizam o preparo
    produtos_from_db = produto_final_model.busca_produtos_preparo(id_preparo=id_preparo, conn=conn)

    for produto in produtos_from_db:
        id_produto = produto[0]
        qtd_preparo = produto[1]

        custo_preparo = preparo_model.busca_custo_preparo(id_preparo, conn)
        # Recalcula o custo do preparo dentro da ficha do produto
        custo = round((float(custo_preparo[1]) / float(custo_preparo[0])) * float(qtd_preparo), 2)

        # Atualiza o custo do preparo na ficha do produto
        produto_final_model.update_produto_preparo(id_produto, id_preparo, custo, conn)

        # Atualiza o custo total do produto
        atualiza_custo_produto(id_produto, conn)

def atualiza_custo_produto(id_produto, conn):
    custo_preparos = produto_final_model.busca_custo_total_preparos(int(id_produto), conn)[0]
    custo_embalagens = produto_final_model.busca_custo_total_embalagens(int(id_produto), conn)[0]

    if custo_preparos == None:
        custo_preparos = 0

    if custo_embalagens == None:
        custo_embalagens = 0

    custo = custo_preparos + custo_embalagens

    produto_final_model.update_custo_produto(custo, id_produto, conn)

@produto_final_bp.route("/novo_produto", methods=["GET", "POST"])
def novo_produto():
    conn = utils.get_db()
    form = forms.ProdutoFinalForm()

    form.unidade_medida.choices = utils.unidade_medida_choices(conn)
    form.tipo_produto.choices = utils.busca_tipos_produto(conn)

    if form.validate_on_submit():
        # Process the form data
        inserted_id = produto_final_model.insert(form.produto_final.data,
                                                 form.tipo_produto.data,
                                                 form.unidade_medida.data,
                                                 form.qtd_produto.data,
                                                 form.preco_venda.data,
                                                 form.descricao.data,
                                                 conn)

        # Redirect to some page
        flash("Produto {} inserido com sucesso".format(request.form.get("produto_final")), "success")

        return redirect(url_for('produto_final_bp.produto_final', id_produto_final=inserted_id))

    return render_template("produto_final/novo_produto.html", form=form)

@produto_final_bp.route("/produto_final/<int:id_produto_final>")
def produto_final(id_produto_final):
    conn = utils.get_db()
    produto_from_db = produto_final_model.busca_dados_produto(id_produto_final, conn)

    try:
        produto = {
            "id": produto_from_db[0],
            "produto": produto_from_db[1],
            "unidade_medida": produto_from_db[2],
            "qtd_produto": produto_from_db[3],
            "custo_produto": produto_from_db[4],
            "preco_venda": produto_from_db[5],
            "descricao": produto_from_db[6]
        }
    except:
        produto = {}

    if produto:
        # busca os preparos que compôem o produto
        produto_preparo_from_db = produto_final_model.busca_produto_preparo(id_produto_final, conn)
        produto_preparo = []

        for row in produto_preparo_from_db:
            row = {
                "id_preparo": row[0],
                "preparo": row[1],
                "qtd_preparo": row[2],
                "id": row[3],
                "unidade_medida": row[4],
                "medida_caseira": row[5],
                "custo_preparo": row[6]

            }
            produto_preparo.append(row)

        produtoPreparoForm = forms.NewProdutoPreparoForm()
        produtoPreparoForm.id_produto.data = id_produto_final

        preparos = [(str(preparo[0]), preparo[1]) for preparo in preparo_model.busca_todos_preparos(conn)]
        produtoPreparoForm.preparo.choices = preparos

        deleteProdutoFinal = forms.DeleteButton()
        deletePreparo = forms.DeleteButton()

        return render_template("produto_final/produto_final.html",
                               produtoPreparoForm=produtoPreparoForm,
                               produto=produto,
                               produto_preparo=produto_preparo,
                               deleteProdutoFinal=deleteProdutoFinal,
                               deletePreparo=deletePreparo)
    return redirect(url_for("index"))

@produto_final_bp.route("/produtopreparo/new", methods=["POST"])
def new_produto_preparo():
    conn = utils.get_db()
    form = forms.NewProdutoPreparoForm()

    preparos = [(str(preparo[0]), preparo[1]) for preparo in preparo_model.busca_todos_preparos(conn)]
    form.preparo.choices = preparos

    if form.validate_on_submit():
        produto_final_model.insert_produto_preparo(form, conn)

        #chama a função para atualizar o custo do produto de acordo com os preparos informados
        atualiza_custo_produto(form.id_produto.data, conn)

    return redirect(url_for('produto_final_bp.produto_final', id_produto_final=form.id_produto.data))

@produto_final_bp.route("/produto_embalagem/<int:id_produto>/new", methods=["GET", "POST"])
def produto_embalagem(id_produto):
    conn = utils.get_db()
    form = forms.ProdutoEmbalagemForm()

    embalagens = [(str(embalagem[0]), embalagem[1]) for embalagem
                  in materia_prima_model.busca_embalagens(id_produto, conn)]
    form.materia_prima.choices = embalagens

    if form.validate_on_submit():
        produto_final_model.insert_produto_embalagem(id_produto,
                                                     form.materia_prima.data,
                                                     form.qtd_materia_prima.data,
                                                     form.custo_material.data,
                                                     conn)

        #chama a função para atualizar o custo do produto de acordo com as embalagens informadas
        atualiza_custo_produto(id_produto, conn)

    produto_embalagem=[]
    embalagens_from_db = produto_final_model.busca_produto_embalagem(id_produto, conn)

    for row in embalagens_from_db:
        embalagem = {
            "id_produto": id_produto,
            "produto_final": row[0],
            "id_materia_prima": row[1],
            "materia_prima": row[2],
            "qtd_materia_prima": row[3],
            "custo_material": row[4],
        }
        produto_embalagem.append(embalagem)

    deleteProdutoEmbalagem= forms.DeleteButton()
    produto_from_db = produto_final_model.busca_dados_produto(id_produto,conn)
    produto_final = produto_from_db[1]

    return render_template("produto_final/produto_embalagem.html",
                           id_produto=id_produto,
                           produto_final=produto_final,
                           produto_embalagem=produto_embalagem,
                           produtoEmbalagemForm=form,
                           deleteProdutoEmbalagem=deleteProdutoEmbalagem)

@produto_final_bp.route("/produtopreparo/<int:id_produto>/<int:id_preparo>/delete", methods=["POST"])
def delete_produto_preparo(id_produto, id_preparo):
    conn = utils.get_db()
    produto_final_model.delete_produto_preparo(id_produto, id_preparo, conn)

    id_produto_str = str(id_produto)
    atualiza_custo_produto(id_produto_str, conn)

    flash("Preparo deletado com sucesso.")

    return redirect(url_for('produto_final_bp.produto_final', id_produto_final=id_produto))

@produto_final_bp.route("/produtoembalagem/<int:id_produto>/<int:id_materia_prima>/delete", methods=["POST"])
def delete_produto_embalagem(id_produto, id_materia_prima):
    conn = utils.get_db()
    produto_final_model.delete_produto_embalagem(id_produto, id_materia_prima, conn)

    id_produto_str = str(id_produto)
    atualiza_custo_produto(id_produto_str, conn)

    flash("Embalagem deletada com sucesso.")

    return redirect(url_for('produto_final_bp.produto_embalagem', id_produto=id_produto))

@produto_final_bp.route("/produtos")
def produtos():
    conn = utils.get_db()
    produtos_db = produto_final_model.busca_todos_produtos(conn)

    produtos = []

    for produto in produtos_db:
        ficha = produto_final_model.ficha_tecnica_existe(produto[0], conn)

        if ficha:
            tem_ficha = True
        else:
            tem_ficha = False

        produto = {
            "id"          : produto[0],
            "produto"     : produto[1],
            "preco_venda" : produto[2],
            "descricao"   : produto[3],
            "tem_ficha"   : tem_ficha
        }
        produtos.append(produto)

    return render_template("produto_final/produtos.html", produtos=produtos)

@produto_final_bp.route("/deleteprodutofinal/<int:id_produto>/delete", methods=["POST"])
def delete_produto_final(id_produto):
    conn = utils.get_db()
    produto_final_model.delete_produto_final(id_produto, conn)

    flash("Produto deletado com sucesso.")

    return redirect(url_for('produto_final_bp.produtos'))