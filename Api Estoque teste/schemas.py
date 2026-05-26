"""
schemas.py
─────────────────────────────────────────────────────────────
Define os "schemas" (modelos de dados) da API usando Pydantic.

Por que usar schemas?
  - Validam automaticamente os dados recebidos (request body)
  - Definem o formato dos dados devolvidos (response)
  - Geram a documentação automática no Swagger UI (/docs)

Schemas definidos:
  ProdutoBase       → campos comuns a criação e atualização
  ProdutoCriar      → body do POST (campos obrigatórios)
  ProdutoAtualizar  → body do PUT  (todos os campos opcionais)
  ProdutoResposta   → formato de retorno da API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ProdutoBase(BaseModel):
    """Campos base compartilhados entre criação e atualização."""
    sku: str = Field(..., max_length=100, example="PROD-001", description="Código único do produto")
    nome: str = Field(..., max_length=255, example="Notebook Dell", description="Nome do produto")
    descricao: Optional[str] = Field(None, example="Notebook com 16GB RAM e SSD 512GB")
    preco_venda: float = Field(..., gt=0, example=3499.90, description="Preço de venda (deve ser maior que 0)")
    ativo: bool = Field(True, example=True, description="Define se o produto está ativo no catálogo")


class ProdutoCriar(ProdutoBase):
    """
    Schema para CRIAR um novo produto (usado no POST).
    Herda todos os campos de ProdutoBase.
    O `id` e `created_at` são gerados pelo banco — não envie esses campos.
    """
    pass


class ProdutoAtualizar(BaseModel):
    """
    Schema para ATUALIZAR um produto (usado no PUT).
    Todos os campos são opcionais: envie apenas o que deseja alterar.
    """
    sku: Optional[str] = Field(None, max_length=100, example="PROD-001-V2")
    nome: Optional[str] = Field(None, max_length=255, example="Notebook Dell Atualizado")
    descricao: Optional[str] = Field(None, example="Nova descrição do produto")
    preco_venda: Optional[float] = Field(None, gt=0, example=3299.90)
    ativo: Optional[bool] = Field(None, example=False)


class ProdutoResposta(ProdutoBase):
    """
    Schema de RESPOSTA da API.
    Inclui os campos gerados pelo banco: `id` e `created_at`.
    """
    id: uuid.UUID = Field(..., description="Identificador único (UUID gerado pelo banco)")
    created_at: datetime = Field(..., description="Data e hora de criação do registro")

    class Config:
        from_attributes = True   # permite converter objetos do banco diretamente para este schema
