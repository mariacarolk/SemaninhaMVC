#encoding: utf-8
import sqlite3
import os

#db_abs_path = os.path.dirname(os.path.realpath(__file__)) + '/semaninha.db'
conn = sqlite3.connect('semaninha.db')
#conn = sqlite3.connect(db_abs_path)
c = conn.cursor()

# As criações de tabela ficarão separadas em funções e serão chamadas ao final do script
# para facilitar caso necessite comentar alguma chamada ou criar apenas algumas tabelas em algum momento

def cria_categoria():
	c.execute("DROP TABLE IF EXISTS categoria")

	c.execute("""CREATE TABLE categoria(
	                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
	                    categoria       TEXT
	)""")

def cria_fornecedor():
	c.execute("DROP TABLE IF EXISTS fornecedor")

	c.execute("""CREATE TABLE fornecedor(
	                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
	                    fornecedor      TEXT
	)""")

def cria_unidade_medida():
	c.execute("DROP TABLE IF EXISTS unidade_medida")

	c.execute("""CREATE TABLE unidade_medida(
	                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
	                    unidade_medida  TEXT
	)""")

def cria_tipo_produto():
	c.execute("DROP TABLE IF EXISTS tipo_produto")

	c.execute("""CREATE TABLE tipo_produto(
	                    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
	                    tipo_produto            TEXT
	)""")

def cria_materia_prima():
	c.execute("DROP TABLE IF EXISTS materia_prima")

	c.execute("""CREATE TABLE materia_prima(
	                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
	                    materia_prima   TEXT,
	                    id_categoria    INTEGER,
	                    id_fornecedor   INTEGER,
	                    id_unid_med     INTEGER,
	                    qtd_embalagem   REAL,
	                    custo_embalagem REAL,
	                    indice_correcao REAL,
	                    fator_coccao    REAL,
	                    custo_final     REAL,
	                    FOREIGN KEY(id_categoria) REFERENCES categoria(id),
	                    FOREIGN KEY(id_fornecedor) REFERENCES fornecedor(id),
	                    FOREIGN KEY(id_unid_med) REFERENCES unidade_medida(id)
	)""")

def cria_clientes():
	c.execute("DROP TABLE IF EXISTS cliente")
	c.execute("""CREATE TABLE cliente(
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome            TEXT,
                    endereco        TEXT,
                    bairro          TEXT,
                    cidade          TEXT,
                    telefone        TEXT,
                    restricoes      TEXT,
                    observacoes     TEXT
)""")

def cria_produto_final():
	c.execute("DROP TABLE IF EXISTS produto_final")
	c.execute("""CREATE TABLE produto_final(
							  id              INTEGER PRIMARY KEY AUTOINCREMENT,
							  produto         TEXT,
							  id_tipo_produto INTEGER,
							  id_unid_med     INTEGER,
							  qtd_produto     REAL,
							  custo_produto   REAL,
							  preco_venda     REAL,
							  descricao       TEXT,
							  FOREIGN KEY(id_unid_med) REFERENCES unidade_medida(id),
							  FOREIGN KEY(id_tipo_produto) REFERENCES tipo_produto(id)
)""")

def cria_preparo():
	c.execute("DROP TABLE IF EXISTS preparo")
	c.execute("""CREATE TABLE preparo(
							  id              INTEGER PRIMARY KEY AUTOINCREMENT,
							  preparo         TEXT,
							  id_unid_med     INTEGER,
							  rendimento      REAL,
							  custo_preparo   REAL,
							  modo_preparo    TEXT,
							  FOREIGN KEY(id_unid_med) REFERENCES unidade_medida(id)
)""")

def cria_preparo_materia_prima():
	c.execute("DROP TABLE IF EXISTS preparo_materia_prima")
	c.execute("""CREATE TABLE preparo_materia_prima(
							  id_preparo          INTEGER,
							  id_materia_prima    INTEGER,
							  qtd_materia_prima   REAL,
							  medida_caseira      TEXT,
							  custo_material      REAL,
							  PRIMARY KEY(id_preparo, id_materia_prima),
							  FOREIGN KEY(id_preparo) REFERENCES preparo(id),
							  FOREIGN KEY(id_materia_prima) REFERENCES materia_prima(id)
)""")

def cria_produto_preparo():
	c.execute("DROP TABLE IF EXISTS produto_preparo")
	c.execute("""CREATE TABLE produto_preparo(
							  id_produto          INTEGER,
							  id_preparo          INTEGER,
							  qtd_preparo         REAL,
							  medida_caseira      TEXT,
							  custo_preparo       REAL,
							  PRIMARY KEY(id_produto, id_preparo),
							  FOREIGN KEY(id_produto) REFERENCES produto_final(id),
							  FOREIGN KEY(id_preparo) REFERENCES preparo(id)
)""")

def cria_pedido():
	c.execute("DROP TABLE IF EXISTS pedido")
	c.execute("""CREATE TABLE pedido(
							  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
							  id_cliente          INTEGER,
							  data_pedido         DATETIME,
							  data_entrega        DATETIME,
							  valor               REAL,
							  status_pagamento    TEXT,
							  status_entrega      TEXT,
							  observacoes         TEXT,
							  FOREIGN KEY(id_cliente) REFERENCES cliente(id)
)""")

def cria_pedido_produto():
	c.execute("DROP TABLE IF EXISTS pedido_produto")
	c.execute("""CREATE TABLE pedido_produto(
							  id_pedido           INTEGER,
							  id_produto          INTEGER,
							  qtd_produto         REAL,
							  PRIMARY KEY(id_pedido, id_produto),
							  FOREIGN KEY(id_pedido) REFERENCES pedido(id),
							  FOREIGN KEY(id_produto) REFERENCES produto_final(id)
)""")

def cria_cardapio():
	c.execute("DROP TABLE IF EXISTS cardapio_periodo")
	c.execute("""CREATE TABLE cardapio_periodo(
							  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
							  data_inicio         DATETIME,
							  data_fim            DATETIME							  
)""")

	c.execute("DROP TABLE IF EXISTS cardapio_produto")
	c.execute("""CREATE TABLE cardapio_produto(
								  id_cardapio       INTEGER,
								  id_produto        INTEGER,
								  imagem            BLOB,
								  observacoes       TEXT,
								  PRIMARY KEY(id_cardapio, id_produto),
								  FOREIGN KEY(id_produto) REFERENCES produto_final(id)
)""")

# Status pagamento - tipo = 'Pagamento'
# Status entrega   - tipo = 'Entrega'
def cria_status():
	c.execute("DROP TABLE IF EXISTS status")

	c.execute("""CREATE TABLE status (
	                id INTEGER PRIMARY KEY AUTOINCREMENT,
	                tipo TEXT NOT NULL,
	                status TEXT NOT NULL,
	                UNIQUE (tipo, status)
	            )""")

def cria_produto_embalagem():
	c.execute("DROP TABLE IF EXISTS produto_embalagem")
	c.execute("""CREATE TABLE produto_embalagem(
							  id_produto           INTEGER,
							  id_materia_prima     INTEGER,
							  qtd_materia_prima    REAL,
							  custo_material       REAL,
							  PRIMARY KEY(id_produto, id_materia_prima),
							  FOREIGN KEY(id_produto) REFERENCES produto_final(id),
							  FOREIGN KEY(id_materia_prima) REFERENCES materia_prima(id)
)""")

def cria_pedido_cliente():
	c.execute("DROP TABLE IF EXISTS pedido_cliente")
	c.execute("""CREATE TABLE pedido_cliente(
							  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
							  nome_cliente        TEXT,
							  endereco            TEXT,
							  data_pedido         DATETIME,
							  data_entrega        DATETIME,
							  valor               REAL,
							  forma_pagamento     TEXT,
							  observacoes         TEXT
)""")

def cria_pedido_cliente_produto():
	c.execute("DROP TABLE IF EXISTS pedido_cliente_produto")
	c.execute("""CREATE TABLE pedido_cliente_produto(
							  id_pedido           INTEGER,
							  id_produto          INTEGER,
							  qtd_produto         REAL,
							  restricoes          TEXT,
							  PRIMARY KEY(id_pedido, id_produto),
							  FOREIGN KEY(id_pedido) REFERENCES pedido_cliente(id),
							  FOREIGN KEY(id_produto) REFERENCES produto_final(id)
)""")

def cria_datas_entrega():
	c.execute("DROP TABLE IF EXISTS datas_entrega")
	c.execute("""CREATE TABLE datas_entrega(
							  data_entrega        DATETIME PRIMARY KEY
)""")


# cria_categoria()
# cria_fornecedor()
# cria_unidade_medida()
# cria_materia_prima()
# cria_clientes()
# cria_produto_final()
# cria_preparo()
# cria_preparo_materia_prima()
#cria_produto_preparo()
# cria_pedido()
#cria_pedido_produto()
# cria_tipo_produto()
#cria_cardapio()
# cria_status()
#cria_produto_embalagem()
# cria_pedido_cliente()
# cria_pedido_cliente_produto()
#cria_datas_entrega()


conn.commit()
conn.close()

print("Banco de dados inicializado e criado.")
