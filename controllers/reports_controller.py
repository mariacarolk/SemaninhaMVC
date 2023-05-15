import os
from flask import Blueprint
from flask import render_template, flash
from Semaninha_MVC.controllers import forms, general_controller
from Semaninha_MVC.models import pedido_model, preparo_model, produto_final_model, utils

# create a blueprint for the cardapio routes
reports_bp = Blueprint('reports_bp', __name__)

@reports_bp.route("/relatorios/lista_compras", methods=["GET","POST"])
def lista_compras():
    conn = utils.get_db()
    form = forms.FiltroPeriodoForm()

    lista_compras = []
    custo_total_compra = 0

    if form.validate_on_submit():
        # Busca os preparos que compõem o pedido (produto pronto)
        preparos_from_db = pedido_model.busca_preparos_pedidos(form.data_inicio.data,
                                                               form.data_fim.data,
                                                               conn)

        utils.create_temp_temp_lista_compras(conn)

        for preparo in preparos_from_db:
            #Busca as matérias primas do preparo (produto cru)
            mp_from_db = preparo_model.busca_mp_preparos(preparo[0], conn)

            for mp in mp_from_db:
                # Calcula a quantidade CRUA de matéria prima necessária para produzir a quantidade de preparo desejada
                # Qtd = quantidade total necessária do preparo * qtd mp necessária para o preparo / rendimento preparo
                qtd_mp = (mp[3] * preparo[2]) / preparo[1]

                # Calcula o custo da máteria prima proporcionalmente a quantidade de preparo desejada
                # Custo = quantidade total necessária do preparo * qtd mp necessária para o preparo / rendimento preparo
                custo_mp = (qtd_mp * mp[4]) / mp[3]

                utils.insert_temp_lista_compras(mp, qtd_mp, custo_mp, conn)

        header = ['Fornecedor',
                  'Matéria Prima',
                  'Unidade medida',
                  'Quantidade',
                  'Custo']

        header_str = ';'.join(header)
        header_str = header_str + '\n'

        subfolder = general_controller.create_subfolder('relat')
        str_filename = 'lista_compras_' + general_controller.return_datetime_str() + '.csv'
        filename = os.path.join(subfolder, str_filename)

        # Writes the csv file
        with open(file=filename, mode='w', encoding='utf8') as csv_file:
            csv_file.write(header_str)

            lista_from_db = utils.busca_temp_lista_compras(conn)

            for row in lista_from_db:
                custo_total_compra += round(row[4],2)

                mp = {
                    "fornecedor"          : row[0],
                    "materia_prima"       : row[1],
                    "unidade_medida"      : row[2],
                    "qtd_materia_prima"   : round(row[3],2),
                    "custo_materia_prima" : round(row[4],2)
                }
                lista_compras.append(mp)

            for cont in range(len(lista_compras)):
                csv_line = lista_compras[cont]['fornecedor'] + ';' \
                           + lista_compras[cont]['materia_prima'] + ';' \
                           + lista_compras[cont]['unidade_medida'] + ';' \
                           + str(lista_compras[cont]['qtd_materia_prima']) + ';' \
                           + str(lista_compras[cont]['custo_materia_prima']) + ';' + '\n'
                csv_file.write(csv_line)

        # Redirect to some page
        flash("Lista de compras gerada com sucesso", "success")

    fornecedor_ativo = ''
    return render_template("reports/lista_compras.html",
                           form=form,
                           lista_compras=lista_compras,
                           fornecedor_ativo=fornecedor_ativo,
                           custo_total_compra=custo_total_compra)

@reports_bp.route("/relatorios/lista_pedidos", methods=["GET","POST"])
def lista_pedidos():
    conn = utils.get_db()
    form = forms.RelatorioPedidoForm()

    subfolder = general_controller.create_subfolder('relat')

    if form.validate_on_submit():
        if form.tipo_relat.data == '1':
            header = ['Nome',
                      'Pedido',
                      'Produto',
                      'Quantidade']
            filename = os.path.join(subfolder, 'cliente_pedido_produto_')
        elif form.tipo_relat.data == '2':
            header = ['Nome',
                      'Produto',
                      'Quantidade']
            filename = os.path.join(subfolder, 'cliente_produto_')
        elif form.tipo_relat.data == '3':
            header = ['Produto',
                      'Quantidade']
            filename = os.path.join(subfolder, 'produto_qtde_')
        elif form.tipo_relat.data == '4':
            header = ['Pedido',
                      'Cliente',
                      'Valor pedido',
                      'Custo pedido']
            filename = os.path.join(subfolder, 'lucratividade_pedidos_')

        header_str = ';'.join(header)
        header_str = header_str + '\n'

        filename = filename + general_controller.return_datetime_str() + '.csv'

        # Writes the csv file
        with open(file=filename, mode='w', encoding='utf8') as csv_file:
            csv_file.write(header_str)

            pedidos_from_db = pedido_model.busca_relat_pedidos(form.data_inicio.data,
                                                               form.data_fim.data,
                                                               form.tipo_relat.data,
                                                               conn)
            for row in pedidos_from_db:
                # CLIENTES X PEDIDOS X PRODUTOS #Tipo 1 c.nome, p.id, pr.produto, pp.qtd_produto
                if form.tipo_relat.data == '1':
                    csv_line = row[0] + ';' \
                               + str(row[1]) + ';' \
                               + row[2] + ';' \
                               + str(row[3]) + ';' + '\n'


                # CLIENTES X PRODUTOS #Tipo 2 c.nome, pr.produto, SUM(pp.qtd_produto)
                if form.tipo_relat.data == '2':
                    csv_line = row[0] + ';' \
                               + str(row[1]) + ';' \
                               + str(row[2]) + ';' + '\n'

                # PRODUTOS X QUANTIDADES #Tipo 3 pr.produto, SUM(pp.qtd_produto)
                if form.tipo_relat.data == '3':
                    csv_line = row[1] + ';' \
                               + str(row[2]) + ';' + '\n'

                # LUCRATIVIDADE DOS PEDIDOS #Tipo 4 p.id, c.nome AS cliente, p.valor, (pp.qtd_produto * pr.custo_produto)
                if form.tipo_relat.data == '4':
                    csv_line = str(row[0]) + ';' \
                               + row[1] + ';' \
                               + str(row[2]) + ';' \
                               + str(round(row[3],2)) + ';' + '\n'

                csv_file.write(csv_line)

        # Redirect to some page
        flash("Lista de pedidos gerada com sucesso", "success")

    return render_template("reports/lista_pedidos.html",
                           form=form)

@reports_bp.route("/relatorios/lista_producao", methods=["GET","POST"])
def lista_producao():
    conn = utils.get_db()
    form = forms.FiltroPeriodoForm()

    if form.validate_on_submit():
        preparos = []

        # Busca os pedidos do banco de dados
        produtos_from_db = pedido_model.busca_relat_pedidos(form.data_inicio.data,
                                                            form.data_fim.data,
                                                            '3',
                                                            conn)

        for row in produtos_from_db:
            id_produto, produto, qtd_produto = row
            preparos_from_db = produto_final_model.busca_produto_preparo(id_produto, conn)

            for preparo in preparos_from_db:
                # Verifica se o preparo já está na lista
                index = next((i for i, d in enumerate(preparos) if d.get('id') == preparo[0]), -1)

                if index > -1:
                    preparos[index]['qtd_preparo'] = preparos[index]['qtd_preparo'] + \
                                                     (preparo[2] * qtd_produto)
                else:
                    prep = {
                        'id': preparo[0],
                        'preparo': preparo[1],
                        'qtd_preparo': preparo[2] * qtd_produto,
                        'unidade_medida': preparo[4]
                    }
                    preparos.append(prep)

        header = ['Preparo',
                  'Quantidade',
                  'Unidade medida']

        header_str = ';'.join(header)
        header_str = header_str + '\n'

        subfolder = general_controller.create_subfolder('relat')
        str_filename = 'lista_producao_' + general_controller.return_datetime_str() + '.csv'
        filename = os.path.join(subfolder, str_filename)

        # Writes the csv file
        with open(file=filename, mode='w', encoding='utf8') as csv_file:
            csv_file.write(header_str)

            for cont in range(len(preparos)):
                csv_line = preparos[cont]['preparo'] + ';' \
                           + str(preparos[cont]['qtd_preparo']) + ';' \
                           + preparos[cont]['unidade_medida'] + ';' + '\n'
                csv_file.write(csv_line)

        # Redirect to some page
        flash("Lista de produção gerada com sucesso", "success")

    return render_template("reports/lista_producao.html",
                           form=form)