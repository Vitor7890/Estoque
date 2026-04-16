"""
schemas.py
─────────────────────────────────────────────────────────────
Modelos de dados (Pydantic) para a API de Estoque
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class EstoqueBase(BaseModel):
    """Campos base compartilhados."""
    sku: str = Field(..., max_length=100, example="EST-001", description="Código único do item de estoque")
    nome: str = Field(..., max_length=255, example="Notebook Dell XPS 15", description="Nome do item")
    descricao: Optional[str] = Field(None, example="Notebook com 16GB RAM, 512GB SSD")
    preco_venda: float = Field(..., gt=0, example=3499.90, description="Preço de venda")
    ativo: bool = Field(True, example=True, description="Item ativo no estoque?")

class EstoqueCriar(EstoqueBase):
    """Usado no POST para criar novo item."""
    pass

class EstoqueAtualizar(BaseModel):
    """Usado no PUT - todos os campos opcionais."""
    sku: Optional[str] = Field(None, max_length=100)
    nome: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None)
    preco_venda: Optional[float] = Field(None, gt=0)
    ativo: Optional[bool] = Field(None)

class EstoqueResposta(EstoqueBase):
    """Resposta completa da API (inclui id e created_at)."""
    id: uuid.UUID = Field(..., description="ID único gerado pelo banco")
    created_at: datetime = Field(..., description="Data de criação")

    class Config:
        from_attributes = True
