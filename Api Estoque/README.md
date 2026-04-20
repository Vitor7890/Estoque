# 📦 API de Controle de Estoque

> Uma API para facilitar o dia a dia do estoque — controle de produtos,
> locais de armazenamento e movimentações de entrada e saída.

## O que essa API faz?

Com ela você consegue:

- 📍 Ver **onde cada produto está guardado**
- 🔢 Saber **quantos itens** existem no momento
- ➕➖ Registrar **entradas e saídas** de produtos
- 📋 Manter um **histórico completo** de todas as movimentações

---

## ✅ O que você precisa ter instalado

Antes de rodar a API, certifique-se de ter:

- **Python** na versão **3.8 ou mais recente**
  - Não sabe se tem? Abra o terminal e digite:
    ```bash
    python --version
    ```
- **PostgreSQL** — o banco de dados usado pela API

---

## 🗂️ O que você pode fazer com a API

A API está dividida em três áreas principais:

---

### 📍 Locais físicos
> São os lugares onde os produtos ficam guardados. Ex: "Prateleira A", "Galpão 2".

- **Criar** um novo local
- **Ver todos** os locais cadastrados
- **Ver um local específico**
- **Editar** as informações de um local
- **Desativar ou excluir** um local

---

### 📦 Estoque
> Controla quais produtos estão em quais locais e em que quantidade.

- **Cadastrar** um produto em um local com uma quantidade inicial
- **Ver tudo** que está no estoque
- **Consultar** quanto tem de um produto (em todos os locais)
- **Aumentar ou diminuir** a quantidade de um produto
- **Remover** um produto do controle de estoque

---

### 🔄 Movimentações
> Registra toda vez que um produto entra ou sai do estoque.

- **Registrar entrada** de um produto
- **Registrar saída** de um produto
- **Ver o histórico completo** de movimentações
- **Adicionar uma observação** — ex: `"compra do mês"`, `"venda para cliente X"`
- **Corrigir** o tipo ou a observação de uma movimentação

> ⚠️ **Atenção:** Se você **excluir** uma movimentação, a quantidade do estoque
> **não volta** ao valor anterior. Se errar, crie uma nova movimentação para corrigir.

---

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

## 🗺️ Rotas disponíveis

> As "rotas" são os endereços que você acessa na API para fazer cada coisa.
> Pense nelas como páginas de um site, mas para dados.

| Endereço              | O que faz                              |
|-----------------------|----------------------------------------|
| `/locais`             | Lista ou cria locais físicos           |
| `/locais/{id}`        | Mostra, edita ou exclui um local       |
| `/estoques`           | Lista ou cria registros de estoque     |
| `/estoques/{id}`      | Mostra, edita ou exclui um estoque     |
| `/movimentacoes`      | Lista ou cria movimentações            |
| `/movimentacoes/{id}` | Mostra, edita ou exclui uma movimentação |
| `/health`             | Verifica se a API e o banco estão ok   |

---

## 🔌 Referência completa das rotas

### 📍 Locais
> Lugares onde você guarda os produtos (prateleira, galpão, etc).

| Método | Endereço | O que faz |
|--------|----------|-----------|
| `GET` | `/locais` | Ver todos os lugares |
| `GET` | `/locais/{id}` | Ver um lugar específico |
| `POST` | `/locais` | Criar um lugar novo |
| `PUT` | `/locais/{id}` | Editar um lugar |
| `DELETE` | `/locais/{id}` | Apagar um lugar |

### 📦 Estoque
> Quantos produtos você tem em cada lugar.

| Método | Endereço | O que faz |
|--------|----------|-----------|
| `GET` | `/estoques` | Ver todo o estoque |
| `GET` | `/estoques/{id}` | Ver um registro específico |
| `GET` | `/estoques/produto/{produto_id}` | Ver estoque de um produto |
| `POST` | `/estoques` | Criar registro de estoque |
| `PUT` | `/estoques/{id}` | Editar um registro |
| `DELETE` | `/estoques/{id}` | Apagar um registro |

### 🔄 Movimentações
> Cada vez que você coloca ou retira produtos do estoque.

| Método | Endereço | O que faz |
|--------|----------|-----------|
| `GET` | `/movimentacoes` | Ver todas as movimentações |
| `GET` | `/movimentacoes/{id}` | Ver uma movimentação |
| `GET` | `/movimentacoes/estoque/{estoque_id}` | Ver movimentações de um estoque |
| `POST` | `/movimentacoes` | Registrar entrada ou saída |
| `PUT` | `/movimentacoes/{id}` | Editar observação |
| `DELETE` | `/movimentacoes/{id}` | Apagar uma movimentação |

---

## 📖 Documentação interativa

Com a API rodando, você pode acessar pelo navegador:

- **`/docs`** → Documentação com exemplos e botões para testar as rotas
- **`/redoc`** → Versão alternativa da documentação, mais detalhada

> 💡 Dica: Esses endereços são ótimos para explorar a API sem precisar
> escrever nenhum código!

---

## 🗂️ Estrutura do projeto

```
estoque/
├── database.py        # Conversa com o banco de dados
├── main.py            # Coração da API
├── schemas.py         # Moldes dos dados (formato esperado)
├── requirements.txt   # Lista do que precisa instalar
└── README.md          # Esse arquivo aqui
```
