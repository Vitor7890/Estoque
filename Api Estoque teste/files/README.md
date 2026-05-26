# 🛒 API REST — Catálogo de Produtos
### Disciplina: Sistemas Distribuídos

---

## 📁 Estrutura do Projeto

```
cat_produtos_api/
├── main.py          # rotas da API (endpoints)
├── database.py      # conexão com o PostgreSQL
├── schemas.py       # modelos de dados (Pydantic)
├── requirements.txt # dependências Python
├── .env.example     # modelo do arquivo de configuração
└── README.md        # este arquivo
```

---

## 🚀 Como executar

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

### 6. Acesse a documentação automática
- Swagger UI → http://localhost:8000/docs
- ReDoc      → http://localhost:8000/redoc

---

## 📌 Endpoints disponíveis

| Método   | Rota                  | Descrição                        |
|----------|-----------------------|----------------------------------|
| `GET`    | `/`                   | Boas-vindas                      |
| `GET`    | `/health`             | Saúde da API e do banco de dados |
| `GET`    | `/produtos`           | Listar todos os produtos         |
| `GET`    | `/produtos/{id}`      | Buscar produto por ID            |
| `POST`   | `/produtos`           | Criar novo produto               |
| `PUT`    | `/produtos/{id}`      | Atualizar produto                |
| `DELETE` | `/produtos/{id}`      | Remover produto                  |

---

## 🗄️ Estrutura da tabela `cat_produtos`

| Campo        | Tipo                     | Descrição                     |
|--------------|--------------------------|-------------------------------|
| `id`         | uuid                     | Chave primária (auto-gerado)  |
| `sku`        | character varying        | Código único do produto       |
| `nome`       | character varying        | Nome do produto               |
| `descricao`  | text                     | Descrição detalhada           |
| `preco_venda`| numeric                  | Preço de venda                |
| `ativo`      | boolean                  | Produto ativo no catálogo?    |
| `created_at` | timestamp with time zone | Data de criação (auto-gerado) |

---

## 🧪 Exemplos de uso (curl)

### Verificar saúde
```bash
curl http://localhost:8000/health
```

### Listar todos os produtos
```bash
curl http://localhost:8000/produtos
```

### Buscar produto por ID
```bash
curl http://localhost:8000/produtos/550e8400-e29b-41d4-a716-446655440000
```

### Criar produto
```bash
curl -X POST http://localhost:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-001",
    "nome": "Notebook Dell",
    "descricao": "Notebook com 16GB RAM",
    "preco_venda": 3499.90,
    "ativo": true
  }'
```

### Atualizar produto (apenas os campos desejados)
```bash
curl -X PUT http://localhost:8000/produtos/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{"preco_venda": 3299.90}'
```

### Deletar produto
```bash
curl -X DELETE http://localhost:8000/produtos/550e8400-e29b-41d4-a716-446655440000
```

---

## 🧠 Conceitos aplicados

- **REST** — arquitetura baseada em recursos e verbos HTTP
- **FastAPI** — framework assíncrono com geração automática de documentação
- **asyncpg** — acesso assíncrono ao PostgreSQL (não bloqueia o servidor)
- **Pool de conexões** — reutilização eficiente de conexões com o banco
- **Pydantic** — validação e serialização automática dos dados
- **UUID** — identificadores únicos universais, ideais para sistemas distribuídos
- **HTTP Status Codes** — 200 OK, 201 Created, 404 Not Found, 400 Bad Request
