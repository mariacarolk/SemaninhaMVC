from Semaninha_MVC.models import utils
from werkzeug.utils import escape
import sqlite3

def busca_todas_mp(conn, id_preparo, id_unid_med):
	c = conn.cursor()

	query = "SELECT * FROM materia_prima "

	if id_preparo:
		query = query + " WHERE id NOT IN (SELECT id_materia_prima " \
						"                    FROM preparo_materia_prima" \
						"					WHERE id_preparo = " + str(id_preparo) + ")" \
						"   AND id_unid_med = " + str(id_unid_med)

	query = query + " ORDER BY materia_prima"

	c.execute(query)
	return c.fetchall()

def busca_dados_mp(id, conn):
	c = conn.cursor()

	c.execute("SELECT mp.id, mp.materia_prima, f.id, mp.id_categoria, mp.id_unid_med, "
			  "       mp.qtd_embalagem, mp.custo_embalagem, mp.indice_correcao,"
			  "       mp.fator_coccao, mp.custo_final"
			  "  FROM materia_prima AS mp"
			  " INNER JOIN fornecedor AS f ON mp.id_fornecedor = f.id"
			  " WHERE mp.id = ?", (id,))

	return c.fetchone()

def busca_embalagens(id, conn):
	c = conn.cursor()

	c.execute("SELECT mp.id, mp.materia_prima "
			  "  FROM materia_prima AS mp"
			  " WHERE mp.id_categoria = 2 "
			  "   AND mp.id NOT IN (SELECT id_materia_prima "
			  "    				      FROM produto_embalagem "
			  "                      WHERE id_produto = ? )",(id,))

	return c.fetchall()

def busca_custo_final_mp(id, conn):
	c = conn.cursor()

	c.execute("""SELECT custo_final 
	                   FROM materia_prima
	                  WHERE id = ? """,
			  (id,)
			  )
	return c.fetchone()

def valida_preparo_mp(id, conn):
	c = conn.cursor()

	c.execute("""SELECT * FROM preparo_materia_prima
	                      WHERE id_materia_prima = ? """,
			  (id,)
			  )
	return c.fetchall()

def busca_dados_mp_completo(id, conn):
	c = conn.cursor()

	c.execute("""SELECT m.id, m.materia_prima, c.categoria, f.fornecedor, u.unidade_medida, 
	                        m.qtd_embalagem, m.custo_embalagem, m.indice_correcao, m.fator_coccao, m.custo_final
	                   FROM materia_prima AS m                  
	                  INNER JOIN unidade_medida AS u ON m.id_unid_med = u.id
	                  INNER JOIN fornecedor AS f ON m.id_fornecedor = f.id
	                  INNER JOIN categoria AS c ON m.id_categoria = c.id
	                  WHERE m.id = ?
	                  ORDER BY m.materia_prima""",
			  (id,))

	return c.fetchone()

def insert(materia_prima, categoria, fornecedor, unidade_medida, qtd_embalagem, custo_embalagem, indice_correcao, fator_coccao, custo_final, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO materia_prima (materia_prima, 
	                                                id_categoria, 
	                                                id_fornecedor, 
	                                                id_unid_med, 
	                                                qtd_embalagem,
	                                                custo_embalagem,
	                                                indice_correcao,
	                                                fator_coccao,
	                                                custo_final)
	                     VALUES(?,?,?,?,?,?,?,?,?)""",
			  (
				  escape(materia_prima),
				  int(categoria),
				  int(fornecedor),
				  int(unidade_medida),
				  float(qtd_embalagem),
				  float(custo_embalagem),
				  float(indice_correcao),
				  float(fator_coccao),
				  float(custo_final),
			  )
			  )
	conn.commit()

def delete_materia_prima(id, conn):
	c = conn.cursor()

	try:
		# Attempt to delete the row with the specified id
		c.execute("DELETE FROM materia_prima WHERE id = ? ", (id,))
		conn.commit()
	except sqlite3.IntegrityError as e:
		conn.rollback()
		raise utils.DeleteError(str(e))

def update(fornecedor, qtd_embalagem, custo_embalagem, indice_correcao, fator_coccao, custo_final, id, conn):
	c = conn.cursor()

	c.execute("""UPDATE materia_prima SET
						id_fornecedor = ?, 
						qtd_embalagem = ?, 
						custo_embalagem = ?, 
						indice_correcao = ?,
						fator_coccao = ?,
						custo_final = ?
				  WHERE id = ?""",
			  (
				  fornecedor,
				  qtd_embalagem,
				  custo_embalagem,
				  indice_correcao,
				  fator_coccao,
				  custo_final,
				  id,
			  )
			  )
	conn.commit()



