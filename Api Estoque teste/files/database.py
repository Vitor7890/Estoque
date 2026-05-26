"""
database.py
─────────────────────────────────────────────────────────────
Módulo responsável pela conexão com o banco de dados PostgreSQL.

Conceito importante — Pool de Conexões:
  Abrir uma nova conexão para cada requisição é lento e caro.
  O pool mantém conexões "prontas" para uso e as reutiliza,
  tornando a API muito mais eficiente.

Funções exportadas:
  criar_pool()  → inicializa o pool (chamado na startup da API)
  fechar_pool() → fecha o pool (chamado no shutdown da API)
  get_pool()    → retorna o pool ativo para uso nas rotas
"""

import asyncpg
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Variável global que armazena o pool de conexões
_pool: asyncpg.Pool | None = None


async def criar_pool() -> None:
    """
    Cria o pool de conexões com o banco de dados.
    Chamada automaticamente quando a API inicia.
    """
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size=2,   # mínimo de conexões sempre abertas
        max_size=10,  # máximo de conexões simultâneas
    )
    print("✅ Pool de conexões criado com sucesso!")


async def fechar_pool() -> None:
    """
    Fecha todas as conexões do pool.
    Chamada automaticamente quando a API encerra.
    """
    global _pool
    if _pool:
        await _pool.close()
        print("🔒 Pool de conexões encerrado.")


def get_pool() -> asyncpg.Pool:
    """
    Retorna o pool de conexões ativo.
    Lança um erro claro se o pool ainda não foi inicializado.
    """
    if _pool is None:
        raise RuntimeError("Pool de conexões não inicializado. Verifique o startup da aplicação.")
    return _pool
