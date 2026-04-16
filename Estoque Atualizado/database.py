"""
database.py
─────────────────────────────────────────────────────────────
Conexão com PostgreSQL usando psycopg2 (síncrono).

Por que psycopg2 em vez de asyncpg?
  - Mais simples de instalar: pip install psycopg2-binary
  - Sem necessidade de async/await
  - Compatível com Flask e qualquer outro framework
  - Funciona igual no VS Code sem configurações extras

Pool de Conexões:
  Reutiliza conexões abertas em vez de abrir uma nova por requisição,
  tornando a API mais eficiente. Aqui usamos SimpleConnectionPool
  do próprio psycopg2, sem dependências extras.
"""

import psycopg2
import psycopg2.pool
import psycopg2.extras  # RealDictCursor: retorna rows como dicionários
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Pool global de conexões
_pool: psycopg2.pool.SimpleConnectionPool | None = None


def criar_pool() -> None:
    """
    Inicializa o pool de conexões.
    Chamada uma vez na inicialização da aplicação.
    """
    global _pool
    _pool = psycopg2.pool.SimpleConnectionPool(
        minconn=2,   # conexões mínimas sempre abertas
        maxconn=10,  # conexões máximas simultâneas
        dsn=os.getenv("DATABASE_URL"),
    )
    print("Pool de conexões criado com sucesso!")


def fechar_pool() -> None:
    """
    Fecha todas as conexões do pool.
    Chamada ao encerrar a aplicação.
    """
    global _pool
    if _pool:
        _pool.closeall()
        print("Pool de conexões encerrado.")


def get_conn():
    """
    Retorna uma conexão do pool.
    Use sempre dentro de um bloco try/finally para devolvê-la.

    Exemplo de uso:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM cat_estoque")
            rows = cur.fetchall()
        finally:
            devolver_conn(conn)
    """
    if _pool is None:
        raise RuntimeError("Pool não inicializado. Verifique a inicialização da aplicação.")
    return _pool.getconn()


def devolver_conn(conn) -> None:
    """Devolve a conexão ao pool após o uso."""
    if _pool:
        _pool.putconn(conn)
