from flask import Blueprint
from flask import jsonify, render_template, request, url_for, flash, redirect
from Semaninha_MVC.models import utils, materia_prima_model, preparo_model, produto_final_model
from Semaninha_MVC.controllers import forms, general_controller, preparo_controller, produto_final_controller

# create a blueprint for materia prima routes
materia_prima_bp = Blueprint('materia_prima_bp', __name__)

def busca_dados_materia_prima(id, conn):
    row = materia_prima_model.busca_dados_mp(id, conn)

    try:
        mp = {
            "id": row[0],
            "materia_prima": row[1],
            "id_fornecedor": row[2],
            "id_categoria": row[3],
            "id_unid_med": row[4],
            "qtd_embalagem": row[5],
            "custo_embalagem": row[6],
            "indice_correcao": row[7],
            "fator_coccao": row[8],
            "custo_final": row[9]
        }
    except:
        mp = {}

    return mp

def calcula_custo_materia_prima(id_materia_prima, qtd_materia_prima):
    conn = utils.get_db()
    custo_final = materia_prima_model.busca_custo_final_mp(id_materia_prima, conn)
    custo_mp = round((float(custo_final[0]) * float(qtd_materia_prima)),2)
    return custo_mp

@materia_prima_bp.route("/nova_materia_prima", methods=["GET", "POST"])
def nova_materia_prima():
    conn = utils.get_db()
    form = forms.MateriaPrimaForm()

    form.categoria.choices = utils.categoria_choices(conn)
    form.unidade_medida.choices = utils.unidade_medida_choices(conn)
    form.fornecedor.choices = utils.fornecedor_choices(conn)

    if form.validate_on_submit():
        materia_prima_model.insert(form.materia_prima.data,
                                   form.categoria.data,
                                   form.fornecedor.data,
                                   form.unidade_medida.data,
                                   form.qtd_embalagem.data,
                                   form.custo_embalagem.data,
                                   form.indice_correcao.data,
                                   form.fator_coccao.data,
                                   form.custo_final.data,
                                   conn)
        # Redirect to some page
        flash("Matéria Prima {} inserida com sucesso".format(request.form.get("materia_prima")), "success")
        return redirect(url_for("materia_prima_bp.materias_primas"))

    return render_template("materia_prima/nova_materia_prima.html", form=form)

@materia_prima_bp.route("/materias_primas")
def materias_primas():
    conn = utils.get_db()
    mp_from_db = materia_prima_model.busca_todas_mp(conn, None, None)

    materias_primas = []

    for mp in mp_from_db:
        materia_prima = {
            "id": mp[0],
            "materia_prima": mp[1],
            "id_categoria": mp[2],
            "id_fornecedor": mp[3],
            "id_unid_med": mp[4],
            "qtd_embalagem": mp[5],
            "custo_embalagem": mp[6],
            "indice_correcao": mp[7],
            "fator_coccao": mp[8],
            "custo_final": mp[9]
        }
        materias_primas.append(materia_prima)

    return render_template("materia_prima/materias_primas.html", materias_primas=materias_primas)

@materia_prima_bp.route("/materia_prima/<int:id>")
def materia_prima(id):
    conn = utils.get_db()
    mp_from_db = materia_prima_model.busca_dados_mp_completo(id, conn)

    try:
        materia_prima = {
                            "id"             : mp_from_db[0],
                            "materia_prima"  : mp_from_db[1],
                            "categoria"      : mp_from_db[2],
                            "fornecedor"     : mp_from_db[3],
                            "unidade_medida" : mp_from_db[4],
                            "qtd_embalagem"  : mp_from_db[5],
                            "custo_embalagem": mp_from_db[6],
                            "indice_correcao": mp_from_db[7],
                            "fator_coccao"   : mp_from_db[8],
                            "custo_final"    : mp_from_db[9]
                        }
    except:
        materia_prima = {}

    deleteMateriaPrima = forms.DeleteButton()

    return render_template("materia_prima/materia_prima.html", mp=materia_prima, deleteMateriaPrima=deleteMateriaPrima)

@materia_prima_bp.route("/materia_prima/<int:id>/delete", methods=["POST"])
def delete_materia_prima(id):
    conn = utils.get_db()
    # Get the list of tables referencing the foreign key column
    tabelas_referencia = general_controller.get_references('materia_prima', 'id')
    general_controller.create_trigger('materia_prima', 'id', tabelas_referencia)

    try:
        # Attempt to delete the row with the specified id
        materia_prima_model.delete_materia_prima(id, conn)
        flash("Matéria prima deletada com sucesso.")
    except utils.DeleteError as e:
        # Handle the integrity error raised by the trigger
        flash(str(e))

    return redirect(url_for('materia_prima_bp.materias_primas'))

@materia_prima_bp.route("/custo_materia_prima/<int:id_materia_prima>/<float(signed=True):qtd_materia_prima>")
def custo_materia_prima(id_materia_prima, qtd_materia_prima):
    custo_mp = calcula_custo_materia_prima(id_materia_prima, qtd_materia_prima)
    return jsonify(custo_mp=custo_mp)

@materia_prima_bp.route("/custo_final_mp/<float(signed=True):custo_embalagem>/<float(signed=True):qtd_embalagem>")
def custo_final_mp(custo_embalagem, qtd_embalagem):
    # calcula o preço por unidade de medida (ex: 1kg, 1l) de acordo com a quantidade na embalagem
    custo_final = custo_embalagem / qtd_embalagem
    return jsonify(custo_final=custo_final)

@materia_prima_bp.route("/materia_prima/<int:id>/edit", methods=["GET", "POST"])
def edit_materia_prima(id):
    conn = utils.get_db()
    form = forms.EditMateriaPrimaForm()

    mp = busca_dados_materia_prima(id, conn)
    form.categoria.choices = utils.categoria_choices(conn)
    form.unidade_medida.choices = utils.unidade_medida_choices(conn)
    form.fornecedor.choices = utils.fornecedor_choices(conn)
    form.materia_prima.data = mp["materia_prima"]
    form.categoria.data = mp["id_categoria"]
    form.unidade_medida.data = mp["id_unid_med"]

    if request.method == 'GET':
        form.fornecedor.data = mp["id_fornecedor"]
        form.qtd_embalagem.data = mp["qtd_embalagem"]
        form.custo_embalagem.data = mp["custo_embalagem"]
        form.indice_correcao.data = mp["indice_correcao"]
        form.fator_coccao.data = mp["fator_coccao"]
        form.custo_final.data = mp["custo_final"]

    if request.method == 'POST':
        if form.validate_on_submit():
            materia_prima_model.update(int(form.fornecedor.data),
                                       float(form.qtd_embalagem.data),
                                       float(form.custo_embalagem.data),
                                       float(form.indice_correcao.data),
                                       float(form.fator_coccao.data),
                                       float(form.custo_final.data),
                                       id,
                                       conn)

            #Atualizar o custo da matéria prima nos preparos e produtos
            #Busca os preparos que utilizam a matéria prima alterada
            preparos_from_db = preparo_model.busca_preparos_mp(id, conn)

            for preparo in preparos_from_db:
                #Busca as informações da matéria prima em questão dentro do preparo
                preparo_from_db = preparo_model.busca_qtd_custo_preparo(id_preparo=preparo[0],
                                                                        id_materia_prima=id,
                                                                        conn=conn)

                qtd_materia_prima = preparo_from_db[0]
                custo_final = materia_prima_model.busca_custo_final_mp(id, conn)
                #Recalcula o custo da matéria prima alterada na ficha técnica
                custo_mp = round((float(custo_final[0]) * float(qtd_materia_prima)), 2)
                preparo_model.atualiza_preparo_materia_prima(id_preparo=preparo[0],
                                                             id_materia_prima=id,
                                                             custo_mp=custo_mp,
                                                             conn=conn)

                #Atualiza o custo total do preparo
                preparo_controller.atualiza_custo_rendimento_preparo(preparo[0], conn)

                #Busca os produtos que utilizam o preparo alterado
                produto_final_controller.atualiza_custo_produto_preparo(id_preparo=preparo[0], conn=conn)


            flash("Matéria prima {} alterada com sucesso".format(form.materia_prima.data), "success")
            return redirect(url_for('materia_prima_bp.materia_prima', id=id))
        else:
            print(form.errors)

    return render_template("materia_prima/edit_materia_prima.html", mp=mp, form=form)