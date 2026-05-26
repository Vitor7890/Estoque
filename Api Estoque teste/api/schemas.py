"""
=============================================================
schemas.py — Modelos de dados (Pydantic)
API REST - Estoque, Local Físico e Movimentação
Disciplina: Sistemas Distribuídos
=============================================================

Cada entidade possui modelos:
  - Base      : campos compartilhados (com validações)
  - Criar     : usado no POST (herda Base)
  - Atualizar : usado no PUT (todos os campos opcionais)
  - Resposta  : retorno completo da API (inclui id e created_at)
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


# =============================================================
# ESTOQUE (cat_estoque)
# Representa o catálogo de itens disponíveis
# =============================================================

class EstoqueBase(BaseModel):
    """Campos base do item de estoque."""
    sku: str = Field(
        ...,
        max_length=100,
        example="EST-001",
        description="Código único do item de estoque",
    )
    nome: str = Field(
        ...,
        max_length=255,
        example="Notebook Dell XPS 15",
        description="Nome do item",
    )
    descricao: Optional[str] = Field(
        None,
        example="Notebook com 16GB RAM, 512GB SSD",
        description="Descrição detalhada do item",
    )
    preco_venda: float = Field(
        ...,
        gt=0,
        example=3499.90,
        description="Preço de venda (deve ser maior que zero)",
    )
    quantidade: int = Field(
        0,
        ge=0,
        example=50,
        description="Quantidade atual disponível em estoque",
    )
    ativo: bool = Field(
        True,
        example=True,
        description="Item ativo no estoque?",
    )


class EstoqueCriar(EstoqueBase):
    """Usado no POST para criar novo item de estoque."""
    pass


class EstoqueAtualizar(BaseModel):
    """Usado no PUT — todos os campos são opcionais."""
    sku: Optional[str] = Field(None, max_length=100, example="EST-001-V2")
    nome: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None)
    preco_venda: Optional[float] = Field(None, gt=0)
    quantidade: Optional[int] = Field(None, ge=0)
    ativo: Optional[bool] = Field(None)


class EstoqueResposta(EstoqueBase):
    """Resposta completa da API (inclui id e created_at)."""
    id: uuid.UUID = Field(..., description="ID único gerado pelo banco")
    created_at: datetime = Field(..., description="Data de criação do registro")

    class Config:
        from_attributes = True


# =============================================================
# LOCAL FÍSICO (cat_local_fisico)
# Representa os locais onde os itens ficam armazenados
# Exemplos: depósito, prateleira, galpão, filial
# =============================================================

class LocalFisicoBase(BaseModel):
    """Campos base do local físico."""
    codigo: str = Field(
        ...,
        max_length=50,
        example="DEP-A1",
        description="Código único do local físico",
    )
    nome: str = Field(
        ...,
        max_length=255,
        example="Depósito Setor A — Prateleira 1",
        description="Nome descritivo do local",
    )
    descricao: Optional[str] = Field(
        None,
        example="Prateleira refrigerada para eletrônicos sensíveis",
        description="Observações sobre o local",
    )
    capacidade_maxima: Optional[int] = Field(
        None,
        ge=1,
        example=200,
        description="Capacidade máxima de itens que o local comporta",
    )
    ativo: bool = Field(
        True,
        example=True,
        description="Local físico está ativo?",
    )


class LocalFisicoCriar(LocalFisicoBase):
    """Usado no POST para criar novo local físico."""
    pass


class LocalFisicoAtualizar(BaseModel):
    """Usado no PUT — todos os campos são opcionais."""
    codigo: Optional[str] = Field(None, max_length=50)
    nome: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None)
    capacidade_maxima: Optional[int] = Field(None, ge=1)
    ativo: Optional[bool] = Field(None)


class LocalFisicoResposta(LocalFisicoBase):
    """Resposta completa da API (inclui id e created_at)."""
    id: uuid.UUID = Field(..., description="ID único gerado pelo banco")
    created_at: datetime = Field(..., description="Data de criação do registro")

    class Config:
        from_attributes = True


# =============================================================
# MOVIMENTAÇÃO (cat_movimentacao)
# Registra entradas e saídas de itens no estoque
# ENTRADA = recebimento/compra | SAIDA = venda/retirada
# Movimentações são imutáveis: sem PUT ou DELETE
# =============================================================

class MovimentacaoBase(BaseModel):
    """Campos base da movimentação de estoque."""
    estoque_id: uuid.UUID = Field(
        ...,
        example="550e8400-e29b-41d4-a716-446655440000",
        description="ID do item de estoque movimentado",
    )
    local_fisico_id: uuid.UUID = Field(
        ...,
        example="660e8400-e29b-41d4-a716-446655440001",
        description="ID do local físico onde ocorreu a movimentação",
    )
    tipo: Literal["ENTRADA", "SAIDA"] = Field(
        ...,
        example="ENTRADA",
        description="Tipo da movimentação: ENTRADA (recebimento) ou SAIDA (retirada)",
    )
    quantidade: int = Field(
        ...,
        gt=0,
        example=10,
        description="Quantidade de itens movimentados (deve ser maior que zero)",
    )
    observacao: Optional[str] = Field(
        None,
        example="Recebimento de fornecedor — NF 12345",
        description="Observação ou justificativa da movimentação",
    )


class MovimentacaoCriar(MovimentacaoBase):
    """Usado no POST para registrar nova movimentação."""
    pass


class MovimentacaoResposta(MovimentacaoBase):
    """
    Resposta completa da API.
    Movimentações são registros históricos — não possuem PUT nem DELETE.
    """
    id: uuid.UUID = Field(..., description="ID único gerado pelo banco")
    created_at: datetime = Field(..., description="Data e hora da movimentação")

    class Config:
        from_attributes = True
