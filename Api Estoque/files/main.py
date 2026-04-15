"""
=============================================================
  API REST - Catálogo de Produtos (cat_produtos)
  Disciplina: Sistemas Distribuídos
=============================================================

Tecnologias utilizadas:
  - FastAPI    : framework web moderno e performático
  - asyncpg   : driver assíncrono para PostgreSQL
  - Pydantic  : validação e serialização de dados
  - Uvicorn   : servidor ASGI

Verbos HTTP implementados:
  GET    /produtos          -> lista todos os produtos
  GET    /produtos/{id}     -> retorna um produto pelo ID (uuid)
  POST   /produtos          -> cria um novo produto
  PUT    /produtos/{id}     -> atualiza um produto existente
  DELETE /produtos/{id}     -> remove um produto

Extras:
  GET    /health            -> verifica saúde da API e banco de dados
  GET    /                  -> mensagem de boas-vindas
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from database import criar_pool, fechar_pool, get_pool
from schemas import ProdutoResposta, ProdutoCriar, ProdutoAtualizar
from typing import List
import uuid


# ─────────────────────────────────────────────
# CICLO DE VIDA DA APLICAÇÃO
# Abre o pool de conexões ao iniciar
# Fecha o pool ao encerrar
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await criar_pool()       # executa ANTES da API começar
    yield
    await fechar_pool()      # executa QUANDO a API encerrar


# ─────────────────────────────────────────────
# INSTÂNCIA PRINCIPAL DA API
# ─────────────────────────────────────────────
app = FastAPI(
    title="API - Catálogo de Produtos",
    description=(
        "API RESTful para gerenciamento da tabela **cat_produtos** no PostgreSQL.\n\n"
        "Desenvolvida como material didático para a disciplina de **Sistemas Distribuídos**."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# ROTA RAIZ  (GET /)
# ─────────────────────────────────────────────
@app.get("/", tags=["Geral"], summary="Boas-vindas")
async def raiz():
    """Rota inicial — confirma que a API está no ar."""
    return {"mensagem": "API de Produtos funcionando! Acesse /docs para ver a documentação."}


# ─────────────────────────────────────────────
# HEALTH CHECK  (GET /health)
# Verifica se a API responde E se o banco está acessível
# ─────────────────────────────────────────────
@app.get("/health", tags=["Geral"], summary="Verificação de saúde")
async def health_check():
    """
    Verifica a saúde da API e da conexão com o banco de dados.

    - **status: ok** — tudo funcionando
    - **status: degradado** — API no ar, mas banco com problema
    """
    pool = get_pool()
    try:
        async with pool.acquire() as conn:
            resultado = await conn.fetchval("SELECT 1")   # query mínima de teste
        db_status = "conectado" if resultado == 1 else "erro"
    except Exception as e:
        db_status = f"erro: {str(e)}"

    status_geral = "ok" if db_status == "conectado" else "degradado"

    return {
        "status": status_geral,
        "api": "online",
        "banco_de_dados": db_status,
    }


# ─────────────────────────────────────────────
# GET ALL  (GET /produtos)
# Retorna todos os produtos da tabela
# ─────────────────────────────────────────────
@app.get(
    "/produtos",
    response_model=List[ProdutoResposta],
    tags=["Produtos"],
    summary="Listar todos os produtos",
)
async def listar_produtos():
    """
    Retorna **todos** os produtos cadastrados na tabela `cat_produtos`.

    Os produtos são ordenados pelo nome em ordem alfabética.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM cat_produtos ORDER BY nome ASC"
        )
    return [dict(row) for row in rows]


# ─────────────────────────────────────────────
# GET BY ID  (GET /produtos/{id})
# Busca um produto específico pelo UUID
# ─────────────────────────────────────────────
@app.get(
    "/produtos/{produto_id}",
    response_model=ProdutoResposta,
    tags=["Produtos"],
    summary="Buscar produto por ID",
)
async def buscar_produto(produto_id: uuid.UUID):
    """
    Retorna **um único produto** identificado pelo seu `id` (UUID).

    - Caso o produto não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM cat_produtos WHERE id = $1", produto_id
        )

    if row is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    return dict(row)


# ─────────────────────────────────────────────
# CREATE  (POST /produtos)
# Insere um novo produto na tabela
# ─────────────────────────────────────────────
@app.post(
    "/produtos",
    response_model=ProdutoResposta,
    status_code=201,
    tags=["Produtos"],
    summary="Criar novo produto",
)
async def criar_produto(produto: ProdutoCriar):
    """
    Cria um **novo produto** na tabela `cat_produtos`.

    - O `id` e o `created_at` são gerados automaticamente pelo banco.
    - O campo `ativo` é `true` por padrão caso não seja informado.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO cat_produtos (sku, nome, descricao, preco_venda, ativo)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            produto.sku,
            produto.nome,
            produto.descricao,
            produto.preco_venda,
            produto.ativo,
        )
    return dict(row)


# ─────────────────────────────────────────────
# UPDATE  (PUT /produtos/{id})
# Atualiza os dados de um produto existente
# ─────────────────────────────────────────────
@app.put(
    "/produtos/{produto_id}",
    response_model=ProdutoResposta,
    tags=["Produtos"],
    summary="Atualizar produto",
)
async def atualizar_produto(produto_id: uuid.UUID, produto: ProdutoAtualizar):
    """
    Atualiza os dados de um produto existente.

    - Apenas os campos **enviados no body** serão alterados (atualização parcial).
    - Caso o produto não exista, retorna **404 Not Found**.
    """
    pool = get_pool()

    # Monta dinamicamente apenas os campos que foram enviados
    campos = produto.model_dump(exclude_unset=True)

    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    # Gera: "sku = $1, nome = $2, ..." e os valores correspondentes
    set_clause = ", ".join(f"{chave} = ${i+1}" for i, chave in enumerate(campos))
    valores = list(campos.values())
    valores.append(produto_id)   # último parâmetro: o WHERE

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE cat_produtos SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores,
        )

    if row is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    return dict(row)


# ─────────────────────────────────────────────
# DELETE  (DELETE /produtos/{id})
# Remove um produto da tabela
# ─────────────────────────────────────────────
@app.delete(
    "/produtos/{produto_id}",
    status_code=200,
    tags=["Produtos"],
    summary="Excluir produto",
)
async def deletar_produto(produto_id: uuid.UUID):
    """
    Remove um produto da tabela `cat_produtos` pelo seu `id`.

    - Caso o produto não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM cat_produtos WHERE id = $1 RETURNING id, nome",
            produto_id,
        )

    if row is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    return {"mensagem": f"Produto '{row['nome']}' removido com sucesso.", "id": str(row["id"])}
