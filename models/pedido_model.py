from Semaninha_MVC.models import utils
from werkzeug.utils import escape

def insert(form, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO pedido
	                     (id_cliente, data_pedido, data_entrega, valor, status_pagamento, status_entrega, observacoes)
	                     VALUES(?,?,?,?,?,?,?)""",
			  (
				  form.cliente.data,
				  form.data_pedido.data,
				  form.data_entrega.data,
				  float(form.valor.data),
				  form.status_pagamento.data,
				  form.status_entrega.data,
				  escape(form.observacoes.data),
			  )
			  )
	conn.commit()

def insert_pedido_produto(form, conn):
	c = conn.cursor()

	c.execute("""INSERT INTO pedido_produto (id_pedido,
	                                                 id_produto,
	                                                 qtd_produto)
	                     VALUES (?,?,?)""",
			  (
				  int(form.id_pedido.data),
				  int(form.produto.data),
				  float(form.qtd_produto.data),
			  )
			  )
	conn.commit()

def delete_pedido(id_pedido, conn):
	c = conn.cursor()

	c.execute("DELETE FROM pedido WHERE id = ? ",
			  (id_pedido,))
	conn.commit()

	delete_pedido_produto(id_pedido, None, conn)

def delete_pedido_produto(id_pedido, id_produto, conn):
	c = conn.cursor()

	query = "DELETE FROM pedido_produto WHERE id_pedido = " + str(id_pedido)

	if id_produto:
		query = query + " AND id_produto = " + str(id_produto)

	c.execute(query)
	conn.commit()

def busca_todos_pedidos(conn):
	c = conn.cursor()

	c.execute("SELECT p.id, "
			  "       c.nome, "
			  "       p.data_pedido, "
			  "       p.data_entrega, "
			  "       p.valor, "
			  "       p.status_pagamento, "
			  "       p.status_entrega"
			  "  FROM pedido AS p "
			  " INNER JOIN cliente AS c ON p.id_cliente = c.id "
			  " ORDER BY p.data_pedido")

	return c.fetchall()

def busca_dados_pedido(id, conn):
	c = conn.cursor()

	c.execute("""SELECT p.id, 
						c.id,
						c.nome, 
						p.data_pedido, 
						p.data_entrega, 
						p.valor, 
						p.status_pagamento, 
						p.status_entrega,
						p.observacoes
				   FROM pedido AS p                  
				  INNER JOIN cliente AS c ON p.id_cliente = c.id
				  WHERE p.id = ? """,
			  (id,))

	return c.fetchone()

def busca_pedido_produto(id, conn):
	c = conn.cursor()

	pedido_produto_from_db = c.execute("""SELECT pp.id_pedido,
	                                             pp.id_produto,
	                                             prod.produto, 
	                                             pp.qtd_produto
	                                         FROM pedido_produto AS pp                                    
	                                        INNER JOIN produto_final AS prod ON pp.id_produto = prod.id
	                                        WHERE pp.id_pedido = ? """, (id,)
									   )

	return pedido_produto_from_db

def busca_relat_pedidos(data_inicio, data_fim, tipo_relat, conn):
	c = conn.cursor()

	if tipo_relat == '1': # CLIENTES X PEDIDOS X PRODUTOS #Tipo 1
		c.execute("""SELECT c.nome, p.id, pr.produto, pp.qtd_produto
						  FROM pedido AS p
						 INNER JOIN pedido_produto AS pp ON p.id = pp.id_pedido 
						 INNER JOIN cliente AS c ON p.id_cliente = c.id
						 INNER JOIN produto_final AS pr ON pp.id_produto = pr.id
					     WHERE p.data_entrega BETWEEN ? and ? 
					     ORDER BY p.id_cliente """,
				  (data_inicio.strftime('%Y-%m-%d'),
				   data_fim.strftime('%Y-%m-%d'),)
				  )

	if tipo_relat == '2': # CLIENTES X PRODUTOS #Tipo 2
		c.execute("""SELECT c.nome, pr.produto, SUM(pp.qtd_produto)
					   FROM pedido AS p
					  INNER JOIN pedido_produto AS pp ON p.id = pp.id_pedido 
					  INNER JOIN cliente AS c ON p.id_cliente = c.id
					  INNER JOIN produto_final AS pr ON pp.id_produto = pr.id
				      WHERE p.data_entrega BETWEEN ? and ? 
				      GROUP BY c.nome, pr.produto """,
				     (data_inicio.strftime('%Y-%m-%d'),
				      data_fim.strftime('%Y-%m-%d'),)
				     )

	if tipo_relat == '3': # PRODUTOS X QUANTIDADES #Tipo 3
		c.execute("""SELECT pr.id, pr.produto, SUM(pp.qtd_produto)
					   FROM pedido AS p
					  INNER JOIN pedido_produto AS pp ON p.id = pp.id_pedido 
					  INNER JOIN produto_final AS pr ON pp.id_produto = pr.id
					  WHERE p.data_entrega BETWEEN ? and ? 
					  GROUP BY pr.produto """,
				     (data_inicio.strftime('%Y-%m-%d'),
				      data_fim.strftime('%Y-%m-%d'),)
				     )

	if tipo_relat == '4': # PEDIDOS X VALOR X CUSTO #Tipo 4
		c.execute("""SELECT p.id, c.nome AS cliente, p.valor, SUM(pp.qtd_produto * pr.custo_produto)
					   FROM pedido AS p
					  INNER JOIN pedido_produto AS pp ON p.id = pp.id_pedido 
					  INNER JOIN produto_final AS pr ON pp.id_produto = pr.id
					  INNER JOIN cliente AS c ON c.id = p.id_cliente
					  WHERE p.data_entrega BETWEEN ? and ? 
					  GROUP BY pp.id_pedido """,
				     (data_inicio.strftime('%Y-%m-%d'),
				      data_fim.strftime('%Y-%m-%d'),)
				     )

	return c.fetchall()

def busca_preparos_pedidos(data_inicio, data_fim, conn):
	c = conn.cursor()

	# Busca os preparos que compõem os pedidos (produto pronto)
	c.execute("""SELECT produto_preparo.id_preparo, 
	                            preparo.rendimento,
	                            (SUM(produto_preparo.qtd_preparo) * pedido_produto.qtd_produto)
	                       FROM pedido_produto 
	                 INNER JOIN pedido ON pedido_produto.id_pedido = pedido.id
	                 INNER JOIN produto_preparo ON pedido_produto.id_produto = produto_preparo.id_produto
	                 INNER JOIN preparo ON produto_preparo.id_preparo = preparo.id
	                      WHERE pedido.data_entrega BETWEEN ? and ?
	                   GROUP BY (produto_preparo.id_preparo)""",
			  (data_inicio.strftime('%Y-%m-%d'),
			   data_fim.strftime('%Y-%m-%d'),)
			  )

	return c.fetchall()