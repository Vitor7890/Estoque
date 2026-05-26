"""
=============================================================
main.py — API REST de Estoque
Disciplina: Sistemas Distribuídos
=============================================================

Entidades gerenciadas:
  - Estoque        (cat_estoque)       → itens do catálogo
  - Local Físico   (cat_local_fisico)  → locais de armazenamento
  - Movimentação   (cat_movimentacao)  → entradas e saídas de itens

Verbos HTTP por entidade:

  ESTOQUE:
    GET    /estoques              → lista todos os itens
    GET    /estoques/{id}         → busca item por ID
    POST   /estoques              → cria novo item
    PUT    /estoques/{id}         → atualiza item existente
    DELETE /estoques/{id}         → remove item

  LOCAL FÍSICO:
    GET    /locais                → lista todos os locais
    GET    /locais/{id}           → busca local por ID
    POST   /locais                → cria novo local
    PUT    /locais/{id}           → atualiza local existente
    DELETE /locais/{id}           → remove local

  MOVIMENTAÇÃO (somente leitura + criação — registros imutáveis):
    GET    /movimentacoes         → lista todas as movimentações
    GET    /movimentacoes/{id}    → busca movimentação por ID
    GET    /movimentacoes/estoque/{estoque_id} → histórico de um item
    POST   /movimentacoes         → registra nova entrada ou saída

  EXTRAS:
    GET /         → boas-vindas
    GET /health   → saúde da API e do banco
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List
import uuid

from database import criar_pool, fechar_pool, get_pool
from schemas import (
    EstoqueCriar, EstoqueAtualizar, EstoqueResposta,
    LocalFisicoCriar, LocalFisicoAtualizar, LocalFisicoResposta,
    MovimentacaoCriar, MovimentacaoResposta,
)


# ─────────────────────────────────────────────
# CICLO DE VIDA DA APLICAÇÃO
# Abre o pool ao iniciar e fecha ao encerrar
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await criar_pool()   # executa ANTES da API começar
    yield
    await fechar_pool()  # executa QUANDO a API encerrar


# ─────────────────────────────────────────────
# INSTÂNCIA PRINCIPAL DA API
# ─────────────────────────────────────────────

app = FastAPI(
    title="API — Estoque, Local Físico e Movimentação",
    description=(
        "API RESTful para gerenciamento de **estoque**, **locais físicos** e "
        "**movimentações** de itens.\n\n"
        "Desenvolvida como material didático para a disciplina de **Sistemas Distribuídos**."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# ROTA RAIZ (GET /)
# ─────────────────────────────────────────────

@app.get("/", tags=["Geral"], summary="Boas-vindas")
async def raiz():
    """Rota inicial — confirma que a API está no ar."""
    return {"mensagem": "API de Estoque funcionando! Acesse /docs para ver a documentação."}


# ─────────────────────────────────────────────
# HEALTH CHECK (GET /health)
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
            resultado = await conn.fetchval("SELECT 1")
        db_status = "conectado" if resultado == 1 else "erro"
    except Exception as e:
        db_status = f"erro: {str(e)}"

    status_geral = "ok" if db_status == "conectado" else "degradado"
    return {
        "status": status_geral,
        "api": "online",
        "banco_de_dados": db_status,
    }


# =============================================================
# ESTOQUE (cat_estoque)
# =============================================================

@app.get(
    "/estoques",
    response_model=List[EstoqueResposta],
    tags=["Estoque"],
    summary="Listar todos os itens de estoque",
)
async def listar_estoques():
    """
    Retorna **todos** os itens cadastrados na tabela `cat_estoque`.

    Os itens são ordenados pelo nome em ordem alfabética.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM cat_estoque ORDER BY nome ASC")
    return [dict(row) for row in rows]


@app.get(
    "/estoques/{estoque_id}",
    response_model=EstoqueResposta,
    tags=["Estoque"],
    summary="Buscar item de estoque por ID",
)
async def buscar_estoque(estoque_id: uuid.UUID):
    """
    Retorna **um único item** de estoque identificado pelo seu `id` (UUID).

    - Caso não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM cat_estoque WHERE id = $1", estoque_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
    return dict(row)


@app.post(
    "/estoques",
    response_model=EstoqueResposta,
    status_code=201,
    tags=["Estoque"],
    summary="Criar novo item de estoque",
)
async def criar_estoque(estoque: EstoqueCriar):
    """
    Cria um **novo item** na tabela `cat_estoque`.

    - O `id` e o `created_at` são gerados automaticamente pelo banco.
    - O campo `ativo` é `true` por padrão caso não seja informado.
    - O campo `quantidade` começa em `0` por padrão.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO cat_estoque (sku, nome, descricao, preco_venda, quantidade, ativo)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            estoque.sku,
            estoque.nome,
            estoque.descricao,
            estoque.preco_venda,
            estoque.quantidade,
            estoque.ativo,
        )
    return dict(row)


@app.put(
    "/estoques/{estoque_id}",
    response_model=EstoqueResposta,
    tags=["Estoque"],
    summary="Atualizar item de estoque",
)
async def atualizar_estoque(estoque_id: uuid.UUID, estoque: EstoqueAtualizar):
    """
    Atualiza os dados de um item de estoque existente.

    - Apenas os campos **enviados no body** serão alterados (atualização parcial).
    - Caso o item não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    campos = estoque.model_dump(exclude_unset=True)

    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    set_clause = ", ".join(f"{chave} = ${i + 1}" for i, chave in enumerate(campos))
    valores = list(campos.values())
    valores.append(estoque_id)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE cat_estoque SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
    return dict(row)


@app.delete(
    "/estoques/{estoque_id}",
    status_code=200,
    tags=["Estoque"],
    summary="Excluir item de estoque",
)
async def deletar_estoque(estoque_id: uuid.UUID):
    """
    Remove um item de estoque pelo seu `id`.

    - Caso não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM cat_estoque WHERE id = $1 RETURNING id, nome",
            estoque_id,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
    return {"mensagem": f"Item '{row['nome']}' removido com sucesso.", "id": str(row["id"])}


# =============================================================
# LOCAL FÍSICO (cat_local_fisico)
# =============================================================

@app.get(
    "/locais",
    response_model=List[LocalFisicoResposta],
    tags=["Local Físico"],
    summary="Listar todos os locais físicos",
)
async def listar_locais():
    """
    Retorna **todos** os locais físicos cadastrados na tabela `cat_local_fisico`.

    Os locais são ordenados pelo nome em ordem alfabética.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM cat_local_fisico ORDER BY nome ASC")
    return [dict(row) for row in rows]


@app.get(
    "/locais/{local_id}",
    response_model=LocalFisicoResposta,
    tags=["Local Físico"],
    summary="Buscar local físico por ID",
)
async def buscar_local(local_id: uuid.UUID):
    """
    Retorna **um único local físico** identificado pelo seu `id` (UUID).

    - Caso não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM cat_local_fisico WHERE id = $1", local_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return dict(row)


@app.post(
    "/locais",
    response_model=LocalFisicoResposta,
    status_code=201,
    tags=["Local Físico"],
    summary="Criar novo local físico",
)
async def criar_local(local: LocalFisicoCriar):
    """
    Cria um **novo local físico** na tabela `cat_local_fisico`.

    - O `id` e o `created_at` são gerados automaticamente pelo banco.
    - O campo `ativo` é `true` por padrão caso não seja informado.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO cat_local_fisico (codigo, nome, descricao, capacidade_maxima, ativo)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            local.codigo,
            local.nome,
            local.descricao,
            local.capacidade_maxima,
            local.ativo,
        )
    return dict(row)


@app.put(
    "/locais/{local_id}",
    response_model=LocalFisicoResposta,
    tags=["Local Físico"],
    summary="Atualizar local físico",
)
async def atualizar_local(local_id: uuid.UUID, local: LocalFisicoAtualizar):
    """
    Atualiza os dados de um local físico existente.

    - Apenas os campos **enviados no body** serão alterados (atualização parcial).
    - Caso o local não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    campos = local.model_dump(exclude_unset=True)

    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    set_clause = ", ".join(f"{chave} = ${i + 1}" for i, chave in enumerate(campos))
    valores = list(campos.values())
    valores.append(local_id)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE cat_local_fisico SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return dict(row)


@app.delete(
    "/locais/{local_id}",
    status_code=200,
    tags=["Local Físico"],
    summary="Excluir local físico",
)
async def deletar_local(local_id: uuid.UUID):
    """
    Remove um local físico pelo seu `id`.

    - Caso não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM cat_local_fisico WHERE id = $1 RETURNING id, nome",
            local_id,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return {"mensagem": f"Local '{row['nome']}' removido com sucesso.", "id": str(row["id"])}


# =============================================================
# MOVIMENTAÇÃO (cat_movimentacao)
# Registros imutáveis — sem PUT e sem DELETE
# =============================================================

@app.get(
    "/movimentacoes",
    response_model=List[MovimentacaoResposta],
    tags=["Movimentação"],
    summary="Listar todas as movimentações",
)
async def listar_movimentacoes():
    """
    Retorna **todas** as movimentações registradas na tabela `cat_movimentacao`.

    Os registros são ordenados da movimentação mais recente para a mais antiga.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM cat_movimentacao ORDER BY created_at DESC"
        )
    return [dict(row) for row in rows]


@app.get(
    "/movimentacoes/{movimentacao_id}",
    response_model=MovimentacaoResposta,
    tags=["Movimentação"],
    summary="Buscar movimentação por ID",
)
async def buscar_movimentacao(movimentacao_id: uuid.UUID):
    """
    Retorna **uma única movimentação** identificada pelo seu `id` (UUID).

    - Caso não exista, retorna **404 Not Found**.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM cat_movimentacao WHERE id = $1", movimentacao_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return dict(row)


@app.get(
    "/movimentacoes/estoque/{estoque_id}",
    response_model=List[MovimentacaoResposta],
    tags=["Movimentação"],
    summary="Histórico de movimentações de um item",
)
async def historico_por_estoque(estoque_id: uuid.UUID):
    """
    Retorna o **histórico completo** de movimentações de um item de estoque específico.

    - Ordenado da movimentação mais recente para a mais antiga.
    - Caso o item não possua movimentações, retorna lista vazia `[]`.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM cat_movimentacao WHERE estoque_id = $1 ORDER BY created_at DESC",
            estoque_id,
        )
    return [dict(row) for row in rows]


@app.post(
    "/movimentacoes",
    response_model=MovimentacaoResposta,
    status_code=201,
    tags=["Movimentação"],
    summary="Registrar nova movimentação",
)
async def criar_movimentacao(movimentacao: MovimentacaoCriar):
    """
    Registra uma **nova movimentação** de estoque na tabela `cat_movimentacao`.

    - **ENTRADA**: aumenta a quantidade do item no estoque.
    - **SAIDA**: diminui a quantidade do item no estoque.
    - Valida se o item de estoque e o local físico existem antes de registrar.
    - Para SAÍDA, valida se há quantidade suficiente disponível.
    - O `id` e o `created_at` são gerados automaticamente pelo banco.

    > ⚠️ Movimentações são **registros históricos imutáveis** — não possuem PUT nem DELETE.
    """
    pool = get_pool()

    async with pool.acquire() as conn:

        # Valida se o item de estoque existe
        estoque = await conn.fetchrow(
            "SELECT id, nome, quantidade FROM cat_estoque WHERE id = $1",
            movimentacao.estoque_id,
        )
        if estoque is None:
            raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")

        # Valida se o local físico existe e está ativo
        local = await conn.fetchrow(
            "SELECT id FROM cat_local_fisico WHERE id = $1 AND ativo = true",
            movimentacao.local_fisico_id,
        )
        if local is None:
            raise HTTPException(
                status_code=404,
                detail="Local físico não encontrado ou inativo.",
            )

        # Para SAÍDA: valida se há quantidade suficiente
        if movimentacao.tipo == "SAIDA":
            if estoque["quantidade"] < movimentacao.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Quantidade insuficiente. "
                        f"Disponível: {estoque['quantidade']} | "
                        f"Solicitado: {movimentacao.quantidade}"
                    ),
                )

        # Registra a movimentação
        row = await conn.fetchrow(
            """
            INSERT INTO cat_movimentacao
                (estoque_id, local_fisico_id, tipo, quantidade, observacao)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            movimentacao.estoque_id,
            movimentacao.local_fisico_id,
            movimentacao.tipo,
            movimentacao.quantidade,
            movimentacao.observacao,
        )

        # Atualiza a quantidade do item no estoque
        if movimentacao.tipo == "ENTRADA":
            await conn.execute(
                "UPDATE cat_estoque SET quantidade = quantidade + $1 WHERE id = $2",
                movimentacao.quantidade,
                movimentacao.estoque_id,
            )
        else:  # SAIDA
            await conn.execute(
                "UPDATE cat_estoque SET quantidade = quantidade - $1 WHERE id = $2",
                movimentacao.quantidade,
                movimentacao.estoque_id,
            )

    return dict(row)
