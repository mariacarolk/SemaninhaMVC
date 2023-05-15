import sqlite3
from werkzeug.utils import escape

class InsertError(Exception):
    pass

class DeleteError(Exception):
    pass

def get_db():
    return sqlite3.connect('db/semaninha.db')

def get_references(reference, conn):
	c = conn.cursor()

	query = f"SELECT name, sql FROM sqlite_master WHERE type='table' AND sql LIKE '%{reference}%'"
	c.execute(query)

	return c.fetchall()

def execute_trigger(trigger_name, table_name, tabela, fk_col_name, conn):
	c = conn.cursor()

	trigger_sql = f"""
        CREATE TRIGGER {trigger_name}
        BEFORE DELETE ON {table_name}
        FOR EACH ROW
        BEGIN
            SELECT CASE
                WHEN (SELECT {tabela[1]} FROM {tabela[0]} WHERE {tabela[1]} = OLD.{fk_col_name}) IS NOT NULL
                    THEN RAISE(ABORT, 'Não é possível deletar o registro {table_name}.{fk_col_name} porque há um registro na tabela {tabela[0]}.{tabela[1]} referenciando este campo.')
            END;
        END;
    """

	# Execute the trigger SQL
	c.execute(trigger_sql)

def trigger_exists(trigger_name, conn):
	c = conn.cursor()

	c.execute(f"SELECT name FROM sqlite_master WHERE type='trigger' AND name='{trigger_name}'")
	return c.fetchone()

def busca_produtos(conn):
    c = conn.cursor()

    c.execute("SELECT id, produto FROM produto_final ORDER BY produto")
    row = c.fetchall()
    return row

def unidade_medida_choices(conn):
    c = conn.cursor()

    c.execute("SELECT id, unidade_medida FROM unidade_medida ORDER BY unidade_medida")

    return c.fetchall()

def busca_tipos_produto(conn):
    c = conn.cursor()

    c.execute("SELECT id, tipo_produto FROM tipo_produto")

    return c.fetchall()

def busca_status_por_tipo(tipo, conn):
	c = conn.cursor()

	c.execute("""SELECT id, status FROM status WHERE tipo = ? ORDER BY tipo, status """,
			  (tipo,))
	return c.fetchall()

def busca_todos_status(conn):
	c = conn.cursor()

	c.execute("SELECT id, tipo, status FROM status ORDER BY tipo, status")

	return c.fetchall()

def busca_status_por_id(id, conn):
	c = conn.cursor()

	c.execute("""SELECT status FROM status WHERE id = ? """,
                  (id,))

	return c.fetchone()[0]

def insert_unid_med(form, conn):
	c = conn.cursor()

	try:
		c.execute("""INSERT INTO unidade_medida (unidade_medida) VALUES(?)""",
				  (escape(form.unidade_medida.data),))
		conn.commit()
	except sqlite3.Error as e:
		conn.rollback()
		raise InsertError(str(e))

def busca_todas_unidades_medida(conn):
	c = conn.cursor()

	c.execute("SELECT id, unidade_medida FROM unidade_medida ORDER BY unidade_medida")

	return c.fetchall()

def insert_tipo_produto(form, conn):
	c = conn.cursor()

	try:
		c.execute("""INSERT INTO tipo_produto (tipo_produto) VALUES(?)""",
				  (escape(form.tipo_produto.data),))
		conn.commit()
	except sqlite3.Error as e:
		conn.rollback()
		raise InsertError(str(e))

def busca_todos_tipos_produto(conn):
	c = conn.cursor()

	c.execute("SELECT id, tipo_produto FROM tipo_produto ORDER BY tipo_produto")
	return c.fetchall()

def insert_status(form, conn):
	c = conn.cursor()

	try:
		c.execute("""INSERT INTO status (tipo, status) VALUES(?, ?)""",
				  (escape(form.tipo.data),
				   escape(form.status.data),))
		conn.commit()
	except sqlite3.Error as e:
		conn.rollback()
		raise InsertError(str(e))

def delete_unid_med(id, conn):
	c = conn.cursor()

	try:
		# Attempt to delete the row with the specified id
		c.execute('DELETE FROM unidade_medida WHERE id = ?', (id,))
		conn.commit()
	except sqlite3.IntegrityError as e:
		conn.rollback()
		raise DeleteError(str(e))

def delete_tipo_produto(id, conn):
	c = conn.cursor()

	try:
		# Attempt to delete the row with the specified id
		c.execute('DELETE FROM tipo_produto WHERE id = ?', (id,))
		conn.commit()
	except sqlite3.IntegrityError as e:
		conn.rollback()
		raise DeleteError(str(e))

def delete_status(id, conn):
	c = conn.cursor()

	try:
		# Attempt to delete the row with the specified id
		c.execute('DELETE FROM status WHERE id = ?', (id,))
		conn.commit()
	except sqlite3.IntegrityError as e:
		conn.rollback()
		raise DeleteError(str(e))

def busca_unidade_medida_por_tipo(id, tipo, conn):
	c = conn.cursor()

	# tipo 1 = materia prima
	# tipo 2 = preparo

	if tipo == 1:
		c.execute("""SELECT u.id, u.unidade_medida 
	                FROM unidade_medida AS u
	          INNER JOIN materia_prima AS m ON m.id_unid_med = u.id
	                  WHERE m.id = ? """,
				  (id,))
	elif tipo == 2:
		c.execute("""SELECT u.id, u.unidade_medida 
	                        FROM unidade_medida AS u
	                  INNER JOIN preparo AS p ON p.id_unid_med = u.id
	                          WHERE p.id = ? """,
				  (id,))

	return c.fetchone()

def create_temp_temp_lista_compras(conn):
	c = conn.cursor()

	c.execute('''CREATE TEMPORARY TABLE temp_lista_compras
	                     (materia_prima TEXT, 
	                      unidade_medida TEXT,
	                      fornecedor TEXT,
	                      qtd_materia_prima FLOAT,
	                      custo_materia_prima FLOAT)''')

def insert_temp_lista_compras(mp, qtd_mp, custo_mp, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO temp_lista_compras (materia_prima,
	                                                             unidade_medida,
	                                                             fornecedor,
	                                                             qtd_materia_prima,
	                                                             custo_materia_prima)
	                                  VALUES (?,?,?,?,?)""",
			  (
				  mp[0],
				  mp[1],
				  mp[2],
				  qtd_mp,
				  custo_mp,
			  )
			  )
	conn.commit()

def busca_temp_lista_compras(conn):
	c = conn.cursor()

	c.execute("""SELECT fornecedor, 
	                                materia_prima,
	                                unidade_medida, 
	                                SUM(qtd_materia_prima), 
	                                SUM(custo_materia_prima)
	                           FROM temp_lista_compras                        
	                       GROUP BY fornecedor, materia_prima
	                       ORDER BY fornecedor, materia_prima"""
			  )

	return c.fetchall()

def categoria_choices(conn):
    c = conn.cursor()

    c.execute("SELECT id, categoria FROM categoria ORDER BY categoria")

    return c.fetchall()

def fornecedor_choices(conn):
    c = conn.cursor()

    c.execute("SELECT id, fornecedor FROM fornecedor ORDER BY fornecedor")

    return c.fetchall()