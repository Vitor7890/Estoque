"""
main.py
=============================================================
  API REST - Catálogo de Estoque (cat_estoque)
  Disciplina: Sistemas Distribuídos - Etapa 3
=============================================================
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from database import criar_pool, fechar_pool, get_pool
from schemas import EstoqueResposta, EstoqueCriar, EstoqueAtualizar
from typing import List
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    await criar_pool()
    yield
    await fechar_pool()

app = FastAPI(
    title="API - Catálogo de Estoque",
    description="API RESTful para gerenciamento da tabela cat_estoque (Etapa 3 - Marketplace)",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/", tags=["Geral"])
async def raiz():
    return {"mensagem": "API de Estoque funcionando! Acesse /docs"}

@app.get("/health", tags=["Geral"])
async def health_check():
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "banco": "conectado"}
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}

@app.get("/estoques", response_model=List[EstoqueResposta], tags=["Estoques"])
async def listar_estoques():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM cat_estoque ORDER BY nome ASC")
    return [dict(row) for row in rows]

@app.get("/estoques/{estoque_id}", response_model=EstoqueResposta, tags=["Estoques"])
async def buscar_estoque(estoque_id: uuid.UUID):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM cat_estoque WHERE id = $1", estoque_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
    return dict(row)

@app.post("/estoques", response_model=EstoqueResposta, status_code=201, tags=["Estoques"])
async def criar_estoque(estoque: EstoqueCriar):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO cat_estoque (sku, nome, descricao, preco_venda, ativo)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            estoque.sku, estoque.nome, estoque.descricao, estoque.preco_venda, estoque.ativo
        )
    return dict(row)

@app.put("/estoques/{estoque_id}", response_model=EstoqueResposta, tags=["Estoques"])
async def atualizar_estoque(estoque_id: uuid.UUID, estoque: EstoqueAtualizar):
    pool = get_pool()
    campos = estoque.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    set_clause = ", ".join(f"{chave} = ${i+1}" for i, chave in enumerate(campos))
    valores = list(campos.values())
    valores.append(estoque_id)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE cat_estoque SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
    return dict(row)

@app.delete("/estoques/{estoque_id}", status_code=200, tags=["Estoques"])
async def deletar_estoque(estoque_id: uuid.UUID):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM cat_estoque WHERE id = $1 RETURNING *",
            estoque_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
    return {"mensagem": "Item de estoque excluído com sucesso."}
