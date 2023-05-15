from Semaninha_MVC.models import utils
from werkzeug.utils import escape

def insert(preparo, id_unid_med, modo_preparo, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO preparo
                 (preparo, id_unid_med, rendimento, custo_preparo, modo_preparo)
                 VALUES(?,?,0.0,0.0,?)""",
                 (
                     escape(preparo),
                     id_unid_med,
                     escape(modo_preparo),
                 )
             )
	conn.commit()
	return c.lastrowid

def insert_preparo_mp(id_preparo, materia_prima, qtd_materia_prima, medida_caseira, custo_material, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO preparo_materia_prima (id_preparo,
	                                                        id_materia_prima,
	                                                        qtd_materia_prima,
	                                                        medida_caseira,
	                                                        custo_material)
	                     VALUES (?,?,?,?,?)""",
			  (
				  int(id_preparo),
				  int(materia_prima),
				  float(qtd_materia_prima),
				  escape(medida_caseira),
				  float(custo_material),
			  )
			  )
	conn.commit()

def busca_todos_preparos(conn):
	c = conn.cursor()

	c.execute("SELECT id, preparo, id_unid_med, rendimento, custo_preparo, modo_preparo"
			  " FROM preparo ORDER BY preparo")
	return c.fetchall()

def busca_dados_preparo(id, conn):
	c = conn.cursor()

	c.execute("""SELECT p.id, p.preparo, u.id, u.unidade_medida, p.rendimento, p.custo_preparo, p.modo_preparo
	                   FROM preparo AS p                  
	                  INNER JOIN unidade_medida AS u ON p.id_unid_med = u.id
	                  WHERE p.id = ?
	                  ORDER BY p.preparo""",
			  (id,))

	return c.fetchone()

# Busca todos os preparos que possuem uma matéria prima específica
def busca_preparos_mp(id_materia_prima, conn):
	c = conn.cursor()

	c.execute("""SELECT id_preparo
	               FROM preparo_materia_prima                
	              WHERE id_materia_prima = ?
	              ORDER BY id_preparo """,
			  (id_materia_prima,))

	return c.fetchall()

def busca_ficha_preparo(id, conn):
	c = conn.cursor()

	ficha_from_db = c.execute("""SELECT f.id_materia_prima,
										m.materia_prima, 
										f.qtd_materia_prima, 
										u.id,
										u.unidade_medida,
										f.medida_caseira, 
										f.custo_material 
								   FROM preparo_materia_prima AS f                                      
								  INNER JOIN materia_prima AS m ON f.id_materia_prima = m.id
								  INNER JOIN unidade_medida AS u ON m.id_unid_med = u.id 
								  WHERE f.id_preparo = ? """,
							      (id,)
							  )
	return ficha_from_db

def busca_qtd_custo_preparo(id_preparo, id_materia_prima, conn):
	c = conn.cursor()

	query = "SELECT ficha.qtd_materia_prima," \
			"       ficha.custo_material," \
			"       mp.indice_correcao, " \
			"       mp.fator_coccao " \
			"  FROM preparo_materia_prima AS ficha " \
			"  INNER JOIN materia_prima AS mp ON ficha.id_materia_prima = mp.id " \
			"  WHERE ficha.id_preparo =  " + str(id_preparo)

	if id_materia_prima:
		query = query + " AND mp.id = " + str(id_materia_prima)
		c.execute(query)
		return c.fetchone()
	else:
		c.execute(query)
		return c.fetchall()

def busca_custo_preparo(id, conn):
	c = conn.cursor()

	c.execute("""SELECT rendimento, custo_preparo 
	                   FROM preparo
	                  WHERE id = ? """,
			  (id,)
			  )
	return c.fetchone()

def busca_mp_preparos(id, conn):
	c = conn.cursor()

	c.execute("""SELECT materia_prima.materia_prima,
	                    unidade_medida.unidade_medida,
	                    fornecedor.fornecedor,
	                    SUM(preparo_materia_prima.qtd_materia_prima), 
	                    SUM(preparo_materia_prima.custo_material)
	                   FROM preparo_materia_prima
	                  INNER JOIN materia_prima ON preparo_materia_prima.id_materia_prima = materia_prima.id
	                  INNER JOIN fornecedor ON materia_prima.id_fornecedor = fornecedor.id
	                  INNER JOIN unidade_medida ON materia_prima.id_unid_med = unidade_medida.id
	                  WHERE preparo_materia_prima.id_preparo = ?
	                  GROUP BY materia_prima.materia_prima
	                  ORDER BY fornecedor.fornecedor, materia_prima.materia_prima""",
			  (id,)
			  )

	return c.fetchall()

def tem_ficha_tecnica(id, conn):
	c = conn.cursor()

	c.execute(" SELECT * "
			  "   FROM preparo_materia_prima "
			  "  WHERE id_preparo =  ? ", (id,))
	return c.fetchone()

def atualiza_rendimento_custo_preparo(qtd_preparo, custo_preparo, id_preparo, conn):
	c = conn.cursor()

	c.execute("""UPDATE preparo SET rendimento = ?, custo_preparo = ? WHERE id = ? """,
			  (qtd_preparo, custo_preparo, id_preparo))
	conn.commit()

def atualiza_preparo_materia_prima(id_preparo, id_materia_prima, custo_mp, conn):
	c = conn.cursor()

	c.execute("""UPDATE preparo_materia_prima 
	                SET custo_material = ?
	 			  WHERE id_preparo = ? 
	 			    AND id_materia_prima = ? """,
			  (custo_mp, id_preparo, id_materia_prima))
	conn.commit()

def delete_preparo_materia_prima(id_preparo, id_materia_prima, conn):
	c = conn.cursor()

	query = "DELETE FROM preparo_materia_prima WHERE id_preparo = " + str(id_preparo)

	if id_materia_prima:
		query = query + " AND id_materia_prima = " + str(id_materia_prima)

	c.execute(query)
	conn.commit()

def delete_preparo(id_preparo, conn):
	c = conn.cursor()

	c.execute("DELETE FROM preparo WHERE id = ? ",
			  (id_preparo,))
	conn.commit()

	delete_preparo_materia_prima(id_preparo, None, conn)

