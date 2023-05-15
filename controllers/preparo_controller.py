from flask import Blueprint
from flask import jsonify, render_template, request, url_for, flash, redirect
from Semaninha_MVC.controllers import forms, produto_final_controller
from Semaninha_MVC.models import utils, preparo_model, materia_prima_model, produto_final_model

# create a blueprint for the preparo routes
preparo_bp = Blueprint('preparo_bp', __name__)

def atualiza_custo_rendimento_preparo(id_preparo, conn):
    ficha = preparo_model.busca_qtd_custo_preparo(id_preparo=id_preparo, id_materia_prima=None, conn=conn)

    qtd_preparo = 0
    custo_preparo = 0

    # calcula o peso final produzido pela receita e o custo
    for materia_prima in ficha:
        qtd_preparo += (materia_prima[0] * materia_prima[3]) / materia_prima[2]
        custo_preparo += materia_prima[1]

    preparo_model.atualiza_rendimento_custo_preparo(qtd_preparo, custo_preparo, id_preparo, conn)

@preparo_bp.route("/novo_preparo", methods=["GET", "POST"])
def novo_preparo():
    conn = utils.get_db()
    form = forms.PreparoForm()

    form.unidade_medida.choices = utils.unidade_medida_choices(conn)

    if form.validate_on_submit():
        id_inserted = preparo_model.insert(form.preparo.data,
                                           form.unidade_medida.data,
                                           form.modo_preparo.data,
                                           conn)

        flash("Preparo {} inserido com sucesso".format(request.form.get("preparo")), "success")
        return redirect(url_for("preparo_bp.preparo", id_preparo=id_inserted))

    return render_template("preparo/novo_preparo.html", form=form)

@preparo_bp.route("/preparos")
def preparos():
    conn = utils.get_db()
    preparos_db = preparo_model.busca_todos_preparos(conn)

    preparos = []

    for preparo in preparos_db:
        ficha = preparo_model.tem_ficha_tecnica(preparo[0], conn)

        if ficha:
            tem_ficha = True
        else:
            tem_ficha = False

        preparo = {
            "id"           : preparo[0],
            "preparo"      : preparo[1],
            "id_unid_med"  : preparo[2],
            "rendimento"   : preparo[3],
            "custo_preparo": preparo[4],
            "modo_preparo" : preparo[5],
            "tem_ficha"    : tem_ficha
        }
        preparos.append(preparo)

    return render_template("preparo/preparos.html", preparos=preparos)

@preparo_bp.route("/preparo/<int:id_preparo>")
def preparo(id_preparo):
    conn = utils.get_db()
    preparo_from_db = preparo_model.busca_dados_preparo(id_preparo, conn)

    try:
        preparo = {
                "id": preparo_from_db[0],
                "preparo": preparo_from_db[1],
                "id_unid_med": preparo_from_db[2],
                "unidade_medida": preparo_from_db[3],
                "rendimento": round(preparo_from_db[4],2),
                "custo_preparo": preparo_from_db[5],
                "modo_preparo": preparo_from_db[6]
            }
    except:
        preparo = {}

    if preparo:
        # busca os dados da ficha tecnica do preparo
        ficha_from_db = preparo_model.busca_ficha_preparo(id_preparo, conn)

        fichas = []

        for row in ficha_from_db:
            row = {
                "id_materia_prima" : row[0],
                "materia_prima"    : row[1],
                "qtd_materia_prima": row[2],
                "id_unid_med"      : row[3],
                "unidade_medida"   : row[4],
                "medida_caseira"   : row[5],
                "custo_material"   : row[6]
            }
            fichas.append(row)

        fichaPreparoForm = forms.NewFichaPreparoForm()
        fichaPreparoForm.id_preparo.data = id_preparo

        materias_primas = [(str(mp[0]), mp[1]) for mp in materia_prima_model.busca_todas_mp(conn, id_preparo, preparo['id_unid_med'])]
        fichaPreparoForm.materia_prima.choices = materias_primas

        deletePreparo = forms.DeleteButton()
        deleteItemFicha = forms.DeleteButton()

        return render_template("preparo/preparo.html",
                               fichaPreparoForm=fichaPreparoForm,
                               preparo=preparo,
                               fichas=fichas,
                               deletePreparo=deletePreparo,
                               deleteItemFicha=deleteItemFicha)
    return redirect(url_for("index"))

@preparo_bp.route("/fichapreparo/new/<int:id_preparo>/<int:id_unid_med>", methods=["POST"])
def new_ficha_preparo(id_preparo, id_unid_med):
    conn = utils.get_db()
    form = forms.NewFichaPreparoForm()

    materias_primas = [(str(mp[0]), mp[1]) for mp in materia_prima_model.busca_todas_mp(conn, id_preparo, id_unid_med)]
    form.materia_prima.choices = materias_primas

    if form.validate_on_submit():
        preparo_model.insert_preparo_mp(form.id_preparo.data,
                                        form.materia_prima.data,
                                        form.qtd_materia_prima.data,
                                        form.medida_caseira.data,
                                        form.custo_material.data,
                                        conn)

        #chama a função para atualizar o custo do preparo de acordo com os ingredientes informados
        atualiza_custo_rendimento_preparo(form.id_preparo.data, conn)

        # Busca os produtos que utilizam o preparo alterado
        produto_final_controller.atualiza_custo_produto_preparo(id_preparo=form.id_preparo.data, conn=conn)

    return redirect(url_for('preparo_bp.preparo', id_preparo=form.id_preparo.data))

@preparo_bp.route("/fichapreparo/<int:id_preparo>/<int:id_materia_prima>/delete", methods=["POST"])
def delete_preparo_materia_prima(id_preparo, id_materia_prima):
    conn = utils.get_db()
    preparo_model.delete_preparo_materia_prima(id_preparo, id_materia_prima, conn)

    id_preparo_str = str(id_preparo)
    atualiza_custo_rendimento_preparo(id_preparo_str, conn)
    # Busca os produtos que utilizam o preparo alterado
    produto_final_controller.atualiza_custo_produto_preparo(id_preparo=id_preparo_str, conn=conn)

    flash("Item da ficha deletado com sucesso.")

    return redirect(url_for('preparo_bp.preparo', id_preparo=id_preparo))

@preparo_bp.route("/deletepreparo/<int:id_preparo>/delete", methods=["POST"])
def delete_preparo(id_preparo):
    conn = utils.get_db()
    preparo_model.delete_preparo(id_preparo, conn)

    flash("Preparo deletado com sucesso.")

    return redirect(url_for('preparo_bp.preparos'))

@preparo_bp.route("/custo_preparo/<int:id_preparo>/<float(signed=True):qtd_preparo>")
def custo_preparo(id_preparo, qtd_preparo):
    conn = utils.get_db()
    custo_preparo = preparo_model.busca_custo_preparo(id_preparo, conn)

    custo = round( ( float(custo_preparo[1]) /float(custo_preparo[0]) ) * float(qtd_preparo),2)
    return jsonify(custo=custo)


