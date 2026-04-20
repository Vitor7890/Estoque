# 📦 API REST — Módulo de Estoque

> Módulo de gerenciamento de estoque responsável pelo controle de produtos em locais físicos e pelo registro de
> movimentações de entrada e saída.
---

## 📁 Estrutura do Projeto

```
estoque_api/
├── main.py          # rotas da API (endpoints)
├── database.py      # conexão com o PostgreSQL
├── schemas.py       # modelos de dados (Pydantic)
├── requirements.txt # dependências Python
└── README.md        # este arquivo
```

## 📋 Descrição

Esta API faz parte de um sistema distribuído maior, sendo responsável pelo **módulo de estoque**. Ela expõe endpoints REST para gerenciar três recursos principais:

- **Locais Físicos** — cadastro e controle de locais de armazenamento.
- **Estoque** — vínculo entre produtos e locais físicos, com controle de quantidade mínima e máxima
- **Movimentações** — registro de entradas e saídas do estoque

---

## 🚀 Como executar

Antes de executar, certifique-se de ter:

- **Python** na versão mais recente
- **PostgreSQL** — o banco de dados usado pela API

---

### 1. Clone ou baixe o projeto

### 2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env e coloque sua senha do banco
```

### 5. Execute a API
```bash
uvicorn main:app --reload
```

## ⚠️ Regras importantes

A API segue algumas regras automáticas para evitar erros:

- 🚫 **Quantidade nunca fica negativa**
  - Se tentar dar saída de mais itens do que o estoque tem,
    a API avisa o erro e **não deixa a operação acontecer**

- 🏠 **Não é possível excluir um local que ainda tem produtos**
  - Primeiro mova ou remova os produtos, depois exclua o local

- 🔁 **Toda movimentação precisa ser de um tipo definido**
  - Apenas **entrada** ou **saída** são aceitos

---

## 📌 Endpoints disponíveis

| Endereço              | O que faz                              |
|-----------------------|----------------------------------------|
| `/locais`             | Lista ou cria locais físicos           |
| `/locais/{id}`        | Mostra, edita ou exclui um local       |
| `/estoques`           | Lista ou cria registros de estoque     |
| `/estoques/{id}`      | Mostra, edita ou exclui um estoque     |
| `/movimentacoes`      | Lista ou cria movimentações            |
| `/movimentacoes/{id}` | Mostra, edita ou exclui uma movimentação |
| `/health`             | Verifica a saude da API e do banco|

---

### Geral
| Método  | Rota      | Descrição                        |
|---------|-----------|----------------------------------|
| `GET`   | `/health` | Saúde da API e do banco de dados |

### Local Físico
| Método   | Rota              | Descrição                        |
|----------|-------------------|----------------------------------|
| `GET`    | `/locais`         | Listar todos os locais           |
| `GET`    | `/locais/{id}`    | Buscar local por ID              |
| `POST`   | `/locais`         | Criar novo local físico          |
| `PUT`    | `/locais/{id}`    | Atualizar local físico           |
| `DELETE` | `/locais/{id}`    | Remover local físico             |

### Estoque
| Método   | Rota                          | Descrição                              |
|----------|-------------------------------|----------------------------------------|
| `GET`    | `/estoques`                   | Listar todos os registros de estoque   |
| `GET`    | `/estoques/{id}`              | Buscar registro por ID                 |
| `GET`    | `/estoques/produto/{id}`      | Buscar estoque de um produto específico|
| `POST`   | `/estoques`                   | Criar novo registro de estoque         |
| `PUT`    | `/estoques/{id}`              | Atualizar registro de estoque          |
| `DELETE` | `/estoques/{id}`              | Remover registro de estoque            |

### Movimentações
| Método   | Rota                              | Descrição                              |
|----------|-----------------------------------|----------------------------------------|
| `GET`    | `/movimentacoes`                  | Listar todas as movimentações          |
| `GET`    | `/movimentacoes/{id}`             | Buscar movimentação por ID             |
| `GET`    | `/movimentacoes/estoque/{id}`     | Listar movimentações de um estoque     |
| `POST`   | `/movimentacoes`                  | Registrar entrada ou saída             |
| `PUT`    | `/movimentacoes/{id}`             | Atualizar tipo ou observação           |
| `DELETE` | `/movimentacoes/{id}`             | Remover movimentação do histórico      |

---


