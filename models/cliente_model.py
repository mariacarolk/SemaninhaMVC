from Semaninha_MVC.models import utils
from werkzeug.utils import escape

def busca_todos_clientes(conn):
	c = conn.cursor()

	c.execute("SELECT id, nome, endereco, bairro, cidade, telefone, restricoes, observacoes"
			  "  FROM cliente ORDER BY nome")
	return c.fetchall()

def busca_dados_cliente(id, conn):
	c = conn.cursor()

	c.execute("""SELECT id, nome, endereco, bairro, cidade, telefone, restricoes, observacoes
	                   FROM cliente 
	                  WHERE id = ? """,
			  (id,))

	return c.fetchone()

def busca_pedidos_cliente(id, conn):
	c = conn.cursor()

	# busca os pedidos já realizados pelo cliente
	pedidos_from_db = c.execute(""" SELECT p.id,
	                                               p.data_pedido,
	                                               p.data_entrega,
	                                               p.valor,
	                                               p.status_pagamento,
	                                               p.status_entrega,
	                                               p.observacoes
	                                          FROM pedido AS p
	                                         WHERE p.id_cliente = ? 
	                                         ORDER BY data_pedido """, (id,)
								)

	return pedidos_from_db

def insert(form, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO cliente
	                     (nome, endereco, bairro, cidade, telefone, restricoes, observacoes)
	                     VALUES(?,?,?,?,?,?,?)""",
			  (
				  escape(form.nome.data),
				  escape(form.endereco.data),
				  escape(form.bairro.data),
				  escape(form.cidade.data),
				  escape(form.telefone.data),
				  escape(form.restricoes.data),
				  escape(form.observacoes.data),
			  )
			  )
	conn.commit()

def delete_cliente(id_cliente, conn):
	c = conn.cursor()

	c.execute("DELETE FROM cliente WHERE id = ? ",
			  (id_cliente,))
	conn.commit()
