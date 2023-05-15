from Semaninha_MVC.models import utils
from werkzeug.utils import escape

def insert(produto_final, tipo_produto, unidade_medida, qtd_produto, preco_venda, descricao, conn):
	c = conn.cursor()
	c.execute("""INSERT INTO produto_final
	             (produto, id_tipo_produto, id_unid_med, qtd_produto, custo_produto, preco_venda, descricao)
	             VALUES(?,?,?,?,?,?,?)""",
			  (
				  escape(produto_final),
				  tipo_produto,
				  unidade_medida,
				  float(qtd_produto),
				  0.0,
				  float(preco_venda),
				  escape(descricao),
			  )
			  )
	conn.commit()
	return c.lastrowid

def insert_produto_preparo(form, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO produto_preparo (id_produto,
	                                                  id_preparo,
	                                                  qtd_preparo,
	                                                  medida_caseira,
	                                                  custo_preparo)
	                     VALUES (?,?,?,?,?)""",
			  (
				  int(form.id_produto.data),
				  int(form.preparo.data),
				  float(form.qtd_preparo.data),
				  escape(form.medida_caseira.data),
				  float(form.custo_preparo.data),
			  )
			  )
	conn.commit()

def insert_produto_embalagem(id_produto, id_materia_prima, qtd_materia_prima, custo_material, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO produto_embalagem (id_produto,
											    id_materia_prima,
											    qtd_materia_prima,
											    custo_material)
				      VALUES (?,?,?,?)""",
			  (
				  int(id_produto),
				  int(id_materia_prima),
				  float(qtd_materia_prima),
				  float(custo_material,),
			  )
	)

	conn.commit()

def busca_todos_produtos(conn):
	c = conn.cursor()

	c.execute("SELECT id, produto, preco_venda, descricao FROM produto_final ORDER BY produto")
	return c.fetchall()

def busca_produtos_preparo(id_preparo, conn):
	c = conn.cursor()

	c.execute(""" SELECT id_produto, qtd_preparo
	                FROM produto_preparo 
	               WHERE id_preparo = ? 
	               ORDER BY id_produto """, (id_preparo,))

	return c.fetchall()

def busca_dados_produto(id, conn):
	c = conn.cursor()

	c.execute("""SELECT p.id, p.produto, u.unidade_medida, p.qtd_produto, p.custo_produto, p.preco_venda, p.descricao
	               FROM produto_final AS p                  
	              INNER JOIN unidade_medida AS u ON p.id_unid_med = u.id
	              WHERE p.id = ?
	              ORDER BY p.produto""",
			  (id,))

	return c.fetchone()

def busca_produto_preparo(id, conn):
	c = conn.cursor()

	produto_preparo_from_db = c.execute("""SELECT pp.id_preparo,
	                                              p.preparo, 
	                                              pp.qtd_preparo, 
	                                              u.id,
	                                              u.unidade_medida,
	                                              pp.medida_caseira, 
	                                              pp.custo_preparo 
	                                         FROM produto_preparo AS pp                                    
	                                   INNER JOIN preparo AS p ON pp.id_preparo = p.id
	                                   INNER JOIN unidade_medida AS u ON p.id_unid_med = u.id 
	                                   WHERE pp.id_produto = ? """, (id,)
										)

	return produto_preparo_from_db

def busca_custo_total_preparos(id_produto, conn):
	c = conn.cursor()

	c.execute("SELECT SUM(custo_preparo) "
			  "  FROM produto_preparo "
			  " WHERE id_produto = ? ", (id_produto,))
	return c.fetchone()

def busca_custo_total_embalagens(id_produto, conn):
	c = conn.cursor()

	c.execute("""SELECT SUM(custo_material) FROM produto_embalagem WHERE id_produto = ? """, (id_produto,))
	return c.fetchone()

def update_custo_produto(custo_produto, id_produto, conn):
	c = conn.cursor()
	c.execute("""UPDATE produto_final SET custo_produto = ? WHERE id = ? """,
			  (custo_produto, id_produto))
	conn.commit()

def update_produto_preparo(id_produto, id_preparo, custo_preparo, conn):
	c = conn.cursor()
	c.execute("""UPDATE produto_preparo SET custo_preparo = ? WHERE id_produto = ? AND id_preparo = ? """,
			  (custo_preparo, id_produto, id_preparo))
	conn.commit()

def delete_produto_preparo(id_produto, id_preparo, conn):
	c = conn.cursor()
	c.execute("DELETE FROM produto_preparo WHERE id_produto = ? AND id_preparo = ?",
			  (id_produto, id_preparo,))
	conn.commit()

def ficha_tecnica_existe(id, conn):
	c = conn.cursor()
	# Verifica se o produto possui ficha técnica preenchida
	c.execute(" SELECT * FROM produto_preparo WHERE id_produto =  ? ", (id,))

	return c.fetchone()

def delete_produto_final(id_produto, conn):
	c = conn.cursor()

	c.execute("DELETE FROM produto_final WHERE id = ? ",
			  (id_produto,))
	conn.commit()

def delete_produto_embalagem(id_produto, id_materia_prima, conn):
	c = conn.cursor()

	c.execute("DELETE FROM produto_embalagem WHERE id_produto = ? AND id_materia_prima = ? ",
			  (id_produto,id_materia_prima))
	conn.commit()

def busca_produto_embalagem(id, conn):
	c = conn.cursor()

	c.execute("SELECT p.produto, e.id_materia_prima, mp.materia_prima, e.qtd_materia_prima, e.custo_material "
			  "  FROM produto_embalagem AS e "
	          " INNER JOIN materia_prima AS mp ON mp.id = e.id_materia_prima "
			  " INNER JOIN produto_final AS p ON p.id = e.id_produto "
			  " WHERE e.id_produto = ? ",(id,))

	return c.fetchall()