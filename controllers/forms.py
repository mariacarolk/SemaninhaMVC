from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import FieldList, FormField, HiddenField, StringField, IntegerField, TextAreaField, SubmitField, SelectField, DecimalField, DateField
from wtforms.widgets import Input
from Semaninha_MVC.models import utils, materia_prima_model
from wtforms.validators import InputRequired, DataRequired, ValidationError

class PriceInput(Input):
    input_type = "number"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        kwargs.setdefault("step", "0.01")
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return Markup("""<div class="input-group mb-3">
                    <div class="input-group-prepend">
                        <span class="input-group-text">$</span>
                    </div>
                    <input %s>
        </div>""" % self.html_params(name=field.name, **kwargs))

class PriceField(DecimalField):
    widget = PriceInput()

class DeleteButton(FlaskForm):
    submit      = SubmitField("Delete")

class CardapioProdutoForm(FlaskForm):
    produto      = SelectField('Produto', validators=[InputRequired(), DataRequired()], coerce=int)
    imagem       = StringField('Imagem')
    observacoes  = TextAreaField('Observacoes')
    submit       = SubmitField('Salvar')

class CardapioPeriodoForm(FlaskForm):
    data_inicio = DateField('Data Inicio', validators=[InputRequired(), DataRequired()])
    data_fim    = DateField('Data Fim', validators=[InputRequired(), DataRequired()])
    produtos    = FieldList(FormField(CardapioProdutoForm), min_entries=1)
    submit      = SubmitField('Salvar')

class ProdutoFinalForm(FlaskForm):
    produto_final  = StringField("Produto", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    tipo_produto   = SelectField("Tipo Produto",validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    qtd_produto    = DecimalField("Quantidade", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    unidade_medida = SelectField("Unidade Medida", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    preco_venda    = PriceField("Preço",validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    descricao      = TextAreaField("Descrição")
    submit         = SubmitField("Submit")

class NewProdutoPreparoForm(FlaskForm):
    preparo           = SelectField("Preparo", coerce=int)
    unidade_medida    = StringField("Unid. Med.")
    qtd_preparo       = DecimalField("Qtd. preparo", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=0.0, places=2,  number_format="%0.2f")
    medida_caseira    = StringField("Medida Caseira")
    custo_preparo     = PriceField("Custo", default=0.0, places=2,  number_format="%0.2f")
    id_produto        = HiddenField(validators=[DataRequired()])
    submit            = SubmitField("Submit")

class PedidoForm(FlaskForm):
    cliente          = SelectField("Cliente",validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], coerce=int)
    data_pedido      = DateField("Data Pedido",validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    data_entrega     = DateField("Data Entrega", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    valor            = PriceField("Preço", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    status_pagamento = SelectField("Status Pagamento", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], coerce=int)
    status_entrega   = SelectField("Status Entrega", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], coerce=int)
    observacoes      = TextAreaField("Observações")
    submit           = SubmitField("Submit")

class NewPedidoProdutoForm(FlaskForm):
    produto     = SelectField("Produto", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], coerce=int)
    qtd_produto = IntegerField("Quantidade", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    observacoes = TextAreaField("Observações")
    id_pedido   = HiddenField(validators=[DataRequired()])
    submit      = SubmitField("Submit")


    def validate_materia_prima(self, field):
        conn = utils.get_db()

        row = materia_prima_model.valida_preparo_mp(field.data, conn)

        if row:
            raise ValidationError('Matéria prima já cadastrada para este preparo.')

class ClienteForm(FlaskForm):
    nome        = StringField("Nome", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    endereco    = StringField("Endereço",validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    bairro      = StringField("Bairro", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    cidade      = StringField("Cidade", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    telefone    = StringField("Telefone",validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    restricoes  = TextAreaField("Restrições")
    observacoes = TextAreaField("Observações")
    submit      = SubmitField("Submit")

class UnidMedForm(FlaskForm):
    unidade_medida = StringField("Unidade Medida", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    submit         = SubmitField("Submit")

class TipoProdutoForm(FlaskForm):
    tipo_produto   = StringField("Tipo Produto", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    submit         = SubmitField("Submit")

class StatusForm(FlaskForm):
    tipo     = SelectField("Tipo", choices=['Pagamento', 'Entrega'], validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    status   = StringField("Status", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    submit   = SubmitField("Submit")

class FiltroPeriodoForm(FlaskForm):
    data_inicio = DateField('Data Inicio', validators=[InputRequired(), DataRequired()])
    data_fim    = DateField('Data Fim', validators=[InputRequired(), DataRequired()])
    submit      = SubmitField("Submit")

class RelatorioPedidoForm(FiltroPeriodoForm):
    tipo_relat = SelectField('Tipo relatório', validators=[InputRequired(), DataRequired()],
                             choices=[(1, 'Clientes x Pedidos x Produtos (GERAL)'),
                                      (2, 'Clientes x Produtos (MONTAGEM ENTREGA)'),
                                      (3, 'Produtos x Quantidades (MONTAGEM MARMITAS)'),
                                      (4, 'Lucratividade dos Pedidos')])
    submit = SubmitField("Gerar Relatório")


    def validate(self, extra_validators=None):
        if not super(FiltroPeriodoForm, self).validate():
            return False

        if self.data_inicio.data and self.data_fim.data and self.data_inicio.data > self.data_fim.data:
            self.data_inicio.errors.append("Data inicial deve ser menor que a data final.")
            return False

        return True

class PreparoForm(FlaskForm):
    preparo        = StringField("Preparo", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    unidade_medida = SelectField("Unidade Medida", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    modo_preparo   = TextAreaField("Modo de preparo")
    submit         = SubmitField("Submit")

class MateriaPrimaForm(FlaskForm):
    materia_prima   = StringField("Matéria Prima", validators=[DataRequired("Campo obrigatório")])
    categoria       = SelectField("Categoria", validators=[DataRequired("Campo obrigatório")], coerce=int)
    fornecedor      = SelectField("Fornecedor", validators=[DataRequired("Campo obrigatório")], coerce=int)
    unidade_medida  = SelectField("Unidade Medida", validators=[DataRequired("Campo obrigatório")], coerce=int)
    qtd_embalagem   = DecimalField("Qtd. embalagem", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=0.0, places=2, number_format="%0.2f")
    custo_embalagem = PriceField("Custo Embalagem", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    indice_correcao = DecimalField("Índice correção", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=1.0, places=2, number_format="%0.2f")
    fator_coccao    = DecimalField("Fator de cocção", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=1.0, places=2, number_format="%0.2f")
    custo_final     = PriceField("Custo Final", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    submit          = SubmitField("Submit")

class EditMateriaPrimaForm(MateriaPrimaForm):
    submit = SubmitField("Update item")

class NewFichaPreparoForm(FlaskForm):
    materia_prima     = SelectField("Matéria Prima", coerce=int)
    unidade_medida    = StringField("Unid. Med.")
    qtd_materia_prima = DecimalField("Qtd. matéria prima", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=0.0, places=2,  number_format="%0.2f")
    medida_caseira    = StringField("Medida Caseira")
    custo_material    = PriceField("Custo", default=0.0, places=2,  number_format="%0.2f")
    id_preparo        = HiddenField(validators=[DataRequired()])
    submit            = SubmitField("Submit")

    # def validate_materia_prima(self, field):
    #     conn = get_db()
    #     c = conn.cursor()
    #
    #     c.execute("""SELECT * FROM preparo_materia_prima
    #                   WHERE id_materia_prima = ? """,
    #               (field.data,)
    #               )
    #     row = c.fetchall()
    #
    #     if row:
    #         raise ValidationError('Matéria prima já cadastrada para este preparo.')

class ProdutoEmbalagemForm(FlaskForm):
    materia_prima     = SelectField("Matéria Prima", coerce=int)
    qtd_materia_prima = DecimalField("Qtd. matéria prima", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=0.0, places=2,  number_format="%0.2f")
    custo_material    = PriceField("Custo", default=0.0, places=2,  number_format="%0.2f")
    submit            = SubmitField("Submit")

# class PedidoClienteProdutoForm(FlaskForm):
#     produto     = SelectField('Produto', validators=[InputRequired(), DataRequired()], coerce=int)
#     qtd_produto = DecimalField("Quantidade", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")], default=0.0, places=2,  number_format="%0.2f")
#     restricoes  = TextAreaField('Restrições')
#     submit      = SubmitField('Salvar')

class PedidoClienteForm(FlaskForm):
    nome_cliente    = StringField("Nome", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    endereco        = StringField("Endereço completo", validators=[InputRequired("Campo obrigatório"), DataRequired("Campo obrigatório")])
    data_entrega    = SelectField('Data Entrega', validators=[InputRequired(), DataRequired()])
    forma_pagamento = SelectField('Forma Pagamento', validators=[InputRequired(), DataRequired()],
                                  choices=[(1, 'Pix'),
                                           (2, 'Cartão de crédito via Picpay (link enviado posteriormente)')])
    observacoes     = TextAreaField('Observações do pedido')
    #produtos        = FieldList(FormField(PedidoClienteProdutoForm), min_entries=1)
    submit          = SubmitField('Salvar')

