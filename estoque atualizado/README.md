# 🛍️ Catálogo de Produtos - API

> Uma API simples para gerenciar produtos.  
> Feita para a disciplina de **Sistemas Distribuídos**.

---

## O que essa API faz?

Com ela você consegue:

- 📋 **Listar** todos os produtos cadastrados
- 🔍 **Buscar** um produto pelo código
- ➕ **Criar** um novo produto
- ✏️ **Atualizar** os dados de um produto existente
- 🗑️ **Remover** um produto

---

## 🛠️ Tecnologias usadas

| Ferramenta    | Para que serve                           |
|---------------|------------------------------------------|
| **FastAPI**   | Cria a estrutura da API                  |
| **asyncpg**   | Conecta com o banco de dados             |
| **Pydantic**  | Valida os dados que entram e saem        |
| **Uvicorn**   | Roda a API no ar                         |
| **PostgreSQL**| Banco de dados (instalado separadamente) |

---

## ⚡ Como funciona a conexão com o banco

O sistema não abre uma conexão nova a cada pedido. Ele mantém um
**"estoque" de conexões** sempre prontas — isso deixa tudo mais rápido.

| Nome | O que faz |
|------|-----------|
| `criar_pool()` | Prepara as conexões quando a API inicia |
| `fechar_pool()` | Fecha as conexões quando a API desliga |
| `get_pool()` | Pega uma conexão pronta para usar |

---

## 🗺️ Rotas da API

> As "rotas" são os endereços que você acessa para fazer cada coisa.
> Pense nelas como páginas de um site, mas para dados.

| Método | Endereço | O que faz |
|--------|----------|-----------|
| `GET` | `/` | Mostra uma mensagem de boas-vindas |
| `GET` | `/health` | Mostra se a API e o banco estão no ar |
| `GET` | `/produtos` | Retorna todos os produtos |
| `GET` | `/produtos/{id}` | Retorna um produto específico |
| `POST` | `/produtos` | Cadastra um novo produto |
| `PUT` | `/produtos/{id}` | Atualiza os dados de um produto |
| `DELETE` | `/produtos/{id}` | Remove um produto |

---

## 📦 Como os dados são organizados

**Para criar um produto**, envie esses campos:

| Campo | Tipo | Obrigatório? |
|-------|------|--------------|
| `sku` | Texto | ✅ Sim |
| `nome` | Texto | ✅ Sim |
| `descricao` | Texto | ❌ Opcional |
| `preco_venda` | Número (maior que zero) | ✅ Sim |
| `ativo` | Verdadeiro / Falso | ✅ Sim |

**O que a API devolve** após criar (inclui o que o banco gera automaticamente):

- Todos os campos acima
- `id` — código único gerado pelo banco
- `created_at` — data e hora de criação

> 💡 **Para atualizar** um produto, envie apenas os campos que quiser mudar.
> Não precisa mandar tudo!

---

## ▶️ Como rodar o projeto

**1. Instale as dependências**
```bash
pip install -r requirements.txt
```

**2. Configure o banco de dados**

Crie um arquivo chamado `.env` na pasta do projeto e coloque:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/banco
```
> ⚠️ Substitua `usuario`, `senha` e `banco` pelos dados da sua instalação.

**3. Inicie a API**
```bash
uvicorn main:app --reload
```

**4. Acesse a documentação interativa**

Abra no navegador:
```
http://localhost:8000/docs
```
Lá você pode testar todas as rotas sem precisar escrever nenhum código!

---

## ✅ Verificando se está tudo certo

Acesse `GET /health`. Se tudo estiver funcionando, você vai receber:

```json
{
  "status": "ok",
  "api": "online",
  "banco_de_dados": "conectado"
}
```

---

## 💡 Exemplos de uso

**Criar um produto:**
```bash
POST /produtos
{
  "sku": "PROD-001",
  "nome": "Notebook",
  "descricao": "Notebook rápido com 16GB RAM",
  "preco_venda": 3499.90,
  "ativo": true
}
```

**Buscar um produto pelo ID:**
```bash
GET /produtos/550e8400-e29b-41d4-a716-446655440000
```

**Atualizar só o preço:**
```bash
PUT /produtos/550e8400-e29b-41d4-a716-446655440000
{
  "preco_venda": 3299.90
}
```

---

## 🗂️ Estrutura dos arquivos

```
estoque/
├── main.py            # As rotas e regras da API
├── database.py        # A conexão com o banco de dados
├── schemas.py         # Os formatos dos dados (validação)
├── requirements.txt   # As bibliotecas necessárias
└── teste.py           # Arquivo usado para testar a API durante o desenvolvimento
```
