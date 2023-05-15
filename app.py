#encoding: utf-8
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from controllers.cardapio_controller import cardapio_bp
from controllers.materia_prima_controller import materia_prima_bp
from controllers.cliente_controller import cliente_bp
from controllers.pedido_controller import pedido_bp
from controllers.general_controller import general_bp
from controllers.preparo_controller import preparo_bp
from controllers.produto_final_controller import produto_final_bp
from controllers.reports_controller import reports_bp

app = Flask(__name__)

app.register_blueprint(cardapio_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(materia_prima_bp)
app.register_blueprint(pedido_bp)
app.register_blueprint(general_bp)
app.register_blueprint(preparo_bp)
app.register_blueprint(produto_final_bp)
app.register_blueprint(reports_bp)

app.config['SECRET_KEY'] = 'CACAU1063AM'
csrf = CSRFProtect(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultas')
def consultas():
    return render_template('consultas.html')

@app.route('/cadastros')
def cadastros():
    return render_template('cadastros.html')

@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')

app.run()