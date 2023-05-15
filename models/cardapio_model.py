import sqlite3
from werkzeug.utils import escape

class DeleteError(Exception):
    pass

def insert(form, conn):
	c = conn.cursor()
	c.execute("""INSERT INTO cardapio_periodo
	                     (data_inicio, data_fim)
	                     VALUES(?,?)""",
			  (
				  form.data_inicio.data,
				  form.data_fim.data,
			  ),
			  )

	conn.commit()
	last_id = c.lastrowid

	return last_id

def insert_cardapio_produto(last_id, produto, imagem, observacoes, conn):
	c = conn.cursor()
	c.execute("""INSERT INTO cardapio_produto
	                         (id_cardapio, id_produto, imagem, observacoes)
	             VALUES(?,?,?,?)""",
			  (
				  int(last_id),
				  int(produto),
				  escape(imagem),
				  escape(observacoes),
			  ),
			  )

	conn.commit()

def busca_todos_cardapios(conn):
	c = conn.cursor()

	c.execute("SELECT id, data_inicio, data_fim FROM cardapio_periodo ORDER BY data_inicio")

	return c.fetchall()

def delete_cardapio(id, conn):
	c = conn.cursor()

	try:
		# Attempt to delete the row with the specified id
		c.execute('DELETE FROM cardapio_periodo WHERE id = ?', (id,))
		conn.commit()
	except sqlite3.IntegrityError as e:
		conn.rollback()
		raise DeleteError(str(e))

	try:
		# Attempt to delete the row with the specified id
		c.execute('DELETE FROM cardapio_produto WHERE id_cardapio = ?', (id,))
		conn.commit()
	except sqlite3.IntegrityError as e:
		conn.rollback()
		raise DeleteError(str(e))

def delete_cardapio_produto(id_cardapio, id_produto, conn):
	c = conn.cursor()

	c.execute("DELETE FROM cardapio_produto WHERE id_cardapio = ? AND id_produto = ?",
			  (id_cardapio, id_produto,))
	conn.commit()

def busca_dados_cardapio_completo(id, conn):
	c = conn.cursor()

	c.execute("""SELECT id, data_inicio, data_fim
  				   FROM cardapio_periodo 
                  WHERE id = ? """, (id,))

	cardapio_db = c.fetchone()

	c.execute("""SELECT cp.id_produto, p.produto, cp.observacoes
	  			   FROM cardapio_periodo AS c
	              INNER JOIN cardapio_produto AS cp ON c.id = cp.id_cardapio
	              INNER JOIN produto_final AS p ON p.id = cp.id_produto
	              WHERE c.id = ? """, (id,))

	produtos_db = c.fetchall()

	return cardapio_db, produtos_db

def busca_produtos_cardapio(date, conn):
	c = conn.cursor()

	c.execute(""" SELECT p.id, p.produto, p.qtd_produto, p.preco_venda, p.descricao
			        FROM cardapio_periodo AS c
		      INNER JOIN cardapio_produto AS cp ON cp.id_cardapio = c.id
		      INNER JOIN produto_final AS p ON p.id = cp.id_produto
                   WHERE c.data_inicio <= ?
                     AND c.data_fim >= ?
                ORDER BY p.id_tipo_produto, p.produto """, (date, date,))

	return c.fetchall()

def busca_datas_entrega(date, conn):
	c = conn.cursor()

	c.execute("""SELECT data_entrega, data_entrega
	  			   FROM datas_entrega 
	              WHERE data_entrega > ? 
	              ORDER BY data_entrega """, (date,))

	return c.fetchall()