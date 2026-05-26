"""
=============================================================
database.py — Conexão assíncrona com PostgreSQL
API REST - Estoque, Local Físico e Movimentação
Disciplina: Sistemas Distribuídos
=============================================================

Gerencia o pool de conexões compartilhado pela aplicação.
O pool é criado uma única vez ao iniciar a API (via lifespan)
e encerrado quando a API é desligada.
"""

import asyncpg
import os
import ssl
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

_pool: Optional[asyncpg.Pool] = None


async def criar_pool() -> None:
    """
    Cria o pool de conexões com o PostgreSQL.
    Chamado automaticamente pelo lifespan da API ao iniciar.
    """
    global _pool

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    _pool = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size=2,
        max_size=10,
        ssl=ssl_context,
    )
    print("✅ Pool de conexões criado com sucesso!")


async def fechar_pool() -> None:
    """
    Encerra o pool de conexões.
    Chamado automaticamente pelo lifespan da API ao desligar.
    """
    global _pool
    if _pool:
        await _pool.close()
        print("🔒 Pool de conexões encerrado.")


def get_pool() -> asyncpg.Pool:
    """
    Retorna o pool ativo para ser usado nas rotas.
    Lança RuntimeError se chamado antes do lifespan inicializar o pool.
    """
    if _pool is None:
        raise RuntimeError("Pool de conexões não inicializado.")
    return _pool
