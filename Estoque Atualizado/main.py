"""
main.py
=============================================================
  API REST - Catálogo de Estoque (cat_estoque)
  Disciplina: Sistemas Distribuídos - Etapa 3
=============================================================
  Como rodar:
    1. Instale as dependências:
         pip install flask psycopg2-binary python-dotenv

    2. Crie um arquivo .env com:
         DATABASE_URL=postgresql://usuario:senha@host:5432/banco

    3. Execute:
         python main.py

    A API ficará disponível em http://localhost:5000
=============================================================
"""

from flask import Flask, request, jsonify
import psycopg2.extras
import uuid

from database import criar_pool, fechar_pool, get_conn, devolver_conn
from schemas import validar_estoque_criar, validar_estoque_atualizar, serializar_estoque

app = Flask(__name__)


# ── Inicialização e encerramento do pool ───────────────────

criar_pool()

import atexit
atexit.register(fechar_pool)  # fecha o pool quando a aplicação encerrar


# ── Helper: executa query e devolve conexão automaticamente ─

def executar(query: str, params: tuple = (), fetchone: bool = False, fetchall: bool = False):
    """
    Executa uma query SQL e retorna o resultado.
    Gerencia conexão e cursor automaticamente.
    """
    conn = get_conn()
    try:
        # RealDictCursor faz cada row retornar como dicionário Python
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            conn.commit()
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
    finally:
        devolver_conn(conn)


# ── Rotas Gerais ───────────────────────────────────────────

@app.get("/")
def raiz():
    return jsonify({"mensagem": "API de Estoque funcionando! Acesse /docs"})


@app.get("/health")
def health_check():
    try:
        executar("SELECT 1")
        return jsonify({"status": "ok", "banco": "conectado"})
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500


# ── Rotas de Estoque ───────────────────────────────────────

@app.get("/estoques")
def listar_estoques():
    rows = executar("SELECT * FROM cat_estoque ORDER BY nome ASC", fetchall=True)
    return jsonify([serializar_estoque(r) for r in rows])


@app.get("/estoques/<estoque_id>")
def buscar_estoque(estoque_id: str):
    try:
        uid = uuid.UUID(estoque_id)
    except ValueError:
        return jsonify({"erro": "ID inválido."}), 400

    row = executar("SELECT * FROM cat_estoque WHERE id = %s", (uid,), fetchone=True)
    if row is None:
        return jsonify({"erro": "Item de estoque não encontrado."}), 404
    return jsonify(serializar_estoque(row))


@app.post("/estoques")
def criar_estoque():
    dados = request.get_json(silent=True) or {}

    ok, erro = validar_estoque_criar(dados)
    if not ok:
        return jsonify({"erro": erro}), 400

    row = executar(
        """
        INSERT INTO cat_estoque (sku, nome, descricao, preco_venda, ativo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            dados["sku"],
            dados["nome"],
            dados.get("descricao"),
            float(dados["preco_venda"]),
            dados.get("ativo", True),
        ),
        fetchone=True,
    )
    return jsonify(serializar_estoque(row)), 201


@app.put("/estoques/<estoque_id>")
def atualizar_estoque(estoque_id: str):
    try:
        uid = uuid.UUID(estoque_id)
    except ValueError:
        return jsonify({"erro": "ID inválido."}), 400

    dados = request.get_json(silent=True) or {}

    ok, erro = validar_estoque_atualizar(dados)
    if not ok:
        return jsonify({"erro": erro}), 400

    # Monta a cláusula SET dinamicamente com apenas os campos enviados
    campos = list(dados.keys())
    set_clause = ", ".join(f"{c} = %s" for c in campos)
    valores = [dados[c] for c in campos] + [uid]

    row = executar(
        f"UPDATE cat_estoque SET {set_clause} WHERE id = %s RETURNING *",
        tuple(valores),
        fetchone=True,
    )
    if row is None:
        return jsonify({"erro": "Item de estoque não encontrado."}), 404
    return jsonify(serializar_estoque(row))


@app.delete("/estoques/<estoque_id>")
def deletar_estoque(estoque_id: str):
    try:
        uid = uuid.UUID(estoque_id)
    except ValueError:
        return jsonify({"erro": "ID inválido."}), 400

    row = executar(
        "DELETE FROM cat_estoque WHERE id = %s RETURNING id",
        (uid,),
        fetchone=True,
    )
    if row is None:
        return jsonify({"erro": "Item de estoque não encontrado."}), 404
    return jsonify({"mensagem": "Item de estoque excluído com sucesso."})


# ── Ponto de entrada ───────────────────────────────────────

if __name__ == "__main__":
    # debug=True reinicia automaticamente ao salvar o arquivo (útil no VS Code)
    app.run(debug=True, port=5000)
