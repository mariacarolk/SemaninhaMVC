import datetime
import os
from flask import Blueprint
from flask import jsonify, render_template, request, url_for, flash, redirect
from Semaninha_MVC.controllers.forms import StatusForm, DeleteButton, UnidMedForm, TipoProdutoForm
from Semaninha_MVC.models import utils

# create a blueprint for the cardapio routes
general_bp = Blueprint('general_bp', __name__)

def create_subfolder(folder_name):
    # Get the current working directory
    cwd = os.getcwd()

    # Construct the path to the subfolder
    subfolder = os.path.join(cwd, folder_name)

    # Create the subfolder if it doesn't exist
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    return subfolder


def return_datetime_str():
    current_datetime = datetime.datetime.now()
    timestamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    timestamp = str(timestamp).replace(' ', '')
    return timestamp

def get_references(table_name, fk_col_name):
    conn = utils.get_db()
    reference = f'REFERENCES {table_name}({fk_col_name})'

    result = [row for row in utils.get_references(reference, conn)]

    ref_tables = []

    for table in result:
        table_name = table[0]
        query = table[1]

        fk_col_name = query.split(reference)[0].split("(")[-1].strip()
        fk_col_name = fk_col_name[:-1]

        ref_tables.append((table_name,fk_col_name))
    return ref_tables

def create_trigger(table_name, fk_col_name, tabelas_referencia):
    conn = utils.get_db()
    # Generate the trigger for each referencing table
    for tabela in tabelas_referencia:
        trigger_name = f"fk_{tabela[0]}_{tabela[1]}_{table_name}_trigger"

        trigger_exists = utils.trigger_exists(trigger_name, conn)

        if not trigger_exists:
            utils.execute_trigger(trigger_name, table_name, tabela, fk_col_name, conn)

def busca_tipo_produto(conn):
    tipos_produto_db = utils.busca_todos_tipos_produto(conn)

    tipos_produto = []

    for row in tipos_produto_db:
        tipo = {
            "id": row[0],
            "tipo_produto": row[1]
        }
        tipos_produto.append(tipo)

    return tipos_produto

def busca_unidades_medida(conn):
    unid_med_db = utils.busca_todas_unidades_medida(conn)

    unidades_medida = []

    for row in unid_med_db:
        unid_med = {
            "id": row[0],
            "unidade_medida": row[1]
        }
        unidades_medida.append(unid_med)

    return unidades_medida

def busca_status(tipo, conn):
    if tipo:
        status_db = utils.busca_status_por_tipo(tipo, conn)
        return status_db

    status_db = utils.busca_todos_status(conn)

    all_status = []

    for row in status_db:
        status = {
           "id": row[0],
           "tipo": row[1],
           "status": row[2]
        }

        all_status.append(status)

    return all_status

@general_bp.route("/nova_unid_med", methods=["GET", "POST"])
def nova_unid_med():
    conn = utils.get_db()
    form = UnidMedForm()

    if form.validate_on_submit():
        try:
            utils.insert_unid_med(form, conn)
            flash("Unidade medida {} inserida com sucesso".format(request.form.get("unidade_medida")), "success")
            return redirect(url_for("general_bp.nova_unid_med"))
        except utils.InsertError as e:
            flash("Erro ao inserir unidade de medida: {}".format(str(e)), "error")

    form = UnidMedForm()
    # Busca dados das unidades já cadastradas
    unidades_medida = busca_unidades_medida(conn)
    deleteUnidMed = DeleteButton()

    return render_template("general/nova_unid_med.html",
                            form=form,
                            unidades_medida=unidades_medida,
                            deleteUnidMed=deleteUnidMed)

@general_bp.route("/novo_tipo_produto", methods=["GET", "POST"])
def novo_tipo_produto():
    conn = utils.get_db()
    form = TipoProdutoForm()

    if form.validate_on_submit():
        try:
            utils.insert_tipo_produto(form, conn)
            flash("Tipo de produto {} inserido com sucesso".format(request.form.get("tipo_produto")), "success")
            return redirect(url_for("general_bp.novo_tipo_produto"))
        except utils.InsertError as e:
            flash("Erro ao inserir tipo de produto: {}".format(str(e)), "error")

    form = TipoProdutoForm()
    # Busca dados dos tipos de produto já cadastrados
    tipos_produto = busca_tipo_produto(conn)
    deleteTipoProduto = DeleteButton()

    return render_template("general/novo_tipo_produto.html", form=form, tipos_produto=tipos_produto, deleteTipoProduto=deleteTipoProduto)

@general_bp.route("/novo_status", methods=["GET", "POST"])
def novo_status():
    conn = utils.get_db()
    form = StatusForm()

    if form.validate_on_submit():
        try:
            utils.insert_status(form, conn)
            flash("Status de {} '{}' inserido com sucesso".format(request.form.get("tipo"), request.form.get("status")), "success")
            return redirect(url_for("general_bp.novo_status"))
        except utils.InsertError as e:
            flash("Erro ao inserir status: {}".format(str(e)), "error")

    form = StatusForm()
    # Busca dados dos status já cadastrados
    all_status = busca_status(None, conn)
    deleteStatus = DeleteButton()

    return render_template("general/novo_status.html", form=form, all_status=all_status, deleteStatus=deleteStatus)

@general_bp.route("/delete_unid_med/<int:id>", methods=["POST"])
def delete_unid_med(id):
    conn = utils.get_db()
    # Get the list of tables referencing the foreign key column
    tabelas_referencia = get_references('unidade_medida', 'id')
    create_trigger('unidade_medida', 'id', tabelas_referencia)

    try:
        # Attempt to delete the row with the specified id
        utils.delete_unid_med(id, conn)
        flash('Unidade deletada com sucesso')
    except utils.DeleteError as e:
        flash(str(e))

    # Busca dados das unidades já cadastradas
    unidades_medida = busca_unidades_medida(conn)
    form = UnidMedForm()
    deleteUnidMed = DeleteButton()

    return render_template("general/nova_unid_med.html",
                            form=form,
                            unidades_medida=unidades_medida,
                            deleteUnidMed=deleteUnidMed)

@general_bp.route("/delete_tipo_produto/<int:id>", methods=["POST"])
def delete_tipo_produto(id):
    conn = utils.get_db()
    # Get the list of tables referencing the foreign key column
    tabelas_referencia = get_references('tipo_produto', 'id')
    create_trigger('tipo_produto', 'id', tabelas_referencia)

    try:
        # Attempt to delete the row with the specified id
        utils.delete_tipo_produto(id, conn)
        flash('Tipo de produto deletada com sucesso')
    except utils.DeleteError as e:
        flash(str(e))

    # Busca dados dos tipos de produto já cadastrados
    tipos_produto = busca_tipo_produto(conn)
    form = TipoProdutoForm()
    deleteTipoProduto = DeleteButton()

    return render_template("general/novo_tipo_produto.html", form=form, tipos_produto=tipos_produto,
                            deleteTipoProduto=deleteTipoProduto)

@general_bp.route("/delete_status/<int:id>", methods=["POST"])
def delete_status(id):
    conn = utils.get_db()
    # Get the list of tables referencing the foreign key column
    tabelas_referencia = get_references('status', 'id')
    create_trigger('status', 'id', tabelas_referencia)

    try:
        # Attempt to delete the row with the specified id
        utils.delete_status(id, conn)

        flash('Status deletado com sucesso')
    except utils.DeleteError as e:
        # Handle the integrity error raised by the trigger
        flash(str(e))

    # Busca dados dos status já cadastrados
    all_status = busca_status(None, conn)
    form = StatusForm()
    deleteStatus = DeleteButton()

    return render_template("general/novo_status.html", form=form, all_status=all_status,
                            deleteStatus=deleteStatus)

@general_bp.route("/unid_med/<int:id>/<int:tipo>")
def unid_med(id, tipo):
    conn = utils.get_db()
    # tipo 1 = materia prima
    # tipo 2 = preparo
    unidade_medida = utils.busca_unidade_medida_por_tipo(id, tipo, conn)
    return jsonify(unidade_medida=unidade_medida)

