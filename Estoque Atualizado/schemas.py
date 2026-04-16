"""
schemas.py
─────────────────────────────────────────────────────────────
Validação e estrutura de dados para a API de Estoque.
Usa apenas dataclasses da biblioteca padrão + uuid/datetime.
Sem dependência do Pydantic.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid


# ── Helpers de validação ───────────────────────────────────

def validar_estoque_criar(dados: dict) -> tuple[bool, str]:
    """
    Valida os campos obrigatórios para criar um item.
    Retorna (True, "") se OK, ou (False, "mensagem de erro").
    """
    obrigatorios = ["sku", "nome", "preco_venda"]
    for campo in obrigatorios:
        if campo not in dados or dados[campo] in (None, ""):
            return False, f"Campo obrigatório ausente: '{campo}'"

    if len(dados["sku"]) > 100:
        return False, "Campo 'sku' deve ter no máximo 100 caracteres."
    if len(dados["nome"]) > 255:
        return False, "Campo 'nome' deve ter no máximo 255 caracteres."

    try:
        preco = float(dados["preco_venda"])
        if preco <= 0:
            return False, "Campo 'preco_venda' deve ser maior que zero."
    except (ValueError, TypeError):
        return False, "Campo 'preco_venda' deve ser um número válido."

    return True, ""


def validar_estoque_atualizar(dados: dict) -> tuple[bool, str]:
    """
    Valida os campos opcionais para atualizar um item.
    Retorna (True, "") se OK, ou (False, "mensagem de erro").
    """
    if not dados:
        return False, "Nenhum campo enviado para atualização."

    campos_permitidos = {"sku", "nome", "descricao", "preco_venda", "ativo"}
    for chave in dados:
        if chave not in campos_permitidos:
            return False, f"Campo não permitido: '{chave}'"

    if "sku" in dados and len(dados["sku"]) > 100:
        return False, "Campo 'sku' deve ter no máximo 100 caracteres."
    if "nome" in dados and len(dados["nome"]) > 255:
        return False, "Campo 'nome' deve ter no máximo 255 caracteres."

    if "preco_venda" in dados:
        try:
            preco = float(dados["preco_venda"])
            if preco <= 0:
                return False, "Campo 'preco_venda' deve ser maior que zero."
        except (ValueError, TypeError):
            return False, "Campo 'preco_venda' deve ser um número válido."

    return True, ""


# ── Serialização de linha do banco ─────────────────────────

def serializar_estoque(row: dict) -> dict:
    """
    Converte uma linha do banco para um dict serializável em JSON.
    Trata UUID e datetime que o json.dumps não suporta nativamente.
    """
    resultado = dict(row)
    if isinstance(resultado.get("id"), uuid.UUID):
        resultado["id"] = str(resultado["id"])
    if isinstance(resultado.get("created_at"), datetime):
        resultado["created_at"] = resultado["created_at"].isoformat()
    return resultado
