# Fast_API_Delivery

## FastAPI Backend Completo com Python

API RESTful desenvolvida com **FastAPI**, **SQLAlchemy**, **Alembic** e **SQLite/PostgreSQL**, seguindo boas práticas de autenticação, autorização e estrutura modular.  
Este projeto implementa um backend completo com **cadastro de usuários, pedidos e itens**, incluindo autenticação segura via **JWT**.

---

## 📚 Tecnologias utilizadas

- **Python 3.11+**  
- **FastAPI** — Framework moderno e rápido para APIs REST  
- **Uvicorn** — Servidor ASGI de alto desempenho  
- **SQLAlchemy** — ORM para modelagem e manipulação do banco de dados  
- **Alembic** — Controle de versões e migrações de banco 
- **SQLite/PostgreSQL** - Banco de Dados
- **Passlib / Argon2** — Criptografia de senhas  
- **Python-dotenv** — Gerenciamento de variáveis de ambiente  
- **Pydantic** — Validação de dados  
- **JWT (PyJWT)** — Autenticação com tokens

---

## 🧩 Estrutura do projeto

```text
├── main.py              # Inicialização do FastAPI e inclusão de routers
├── models.py            # Modelos SQLAlchemy (User, Order, OrderItens)
├── schemas.py           # Schemas Pydantic (requests/responses)
├── dependencies.py      # Dependências (JWT, sessões DB)
├── routers/
│   ├── auth_routers.py  # Endpoints de autenticação
│   └── order_routers.py # Endpoints de pedidos e itens
├── .env                 # Variáveis de ambiente
└── requirements.txt
```

## ⚙️ Configuração do ambiente local

### 1. Clone o repositório

```bash
git clone https://github.com/VitorOliP/Fast_API_Delivery.git
cd fastapi-backend
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 🗄️ Configuração do banco de dados

### 4. Crie o arquivo ```.env``` na raiz do projeto

Copie o .env.example e configure suas variáveis:
```bash
cp .env.example .env
```
Exemplo:

```ini
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco
SECRET_KEY=sua_chave_jwt_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📦 Criando e migrando o banco de dados (Alembic + SQLAlchemy)

### 5. Inicialize as migrações

```bash
alembic init alembic
```
(caso o diretório já exista, pule este passo)

### 6. Gere a primeira revisão (criação das tabelas)

```bash
alembic revision --autogenerate -m "create initial tables"
```

### 7. Aplique a migração

```bash
alembic upgrade head
```

## ▶️ Executando o servidor localmente

### 8. Rode o servidor com Uvicorn

```bash
uvicorn app.main:app --reload
```

## 📘 Documentação

A descrição completa de todos os endpoints, parâmetros e modelos de resposta pode ser encontrada diretamente na documentação interativa do Swagger, disponível em:

- Documentação Swagger: http://localhost/docs


## 🔐 Autenticação JWT

O sistema utiliza JSON Web Tokens (JWT) para autenticação.

- Faça login via /auth/login para receber um token.

- Envie o token no header de requisição:

``` makefile
Authorization: Bearer <seu_token>
```

## 🧠 Conceitos aplicados

- Estrutura modular com APIRouter

- Schemas e validações com Pydantic

- CRUD completo (usuário, pedido, item)

- Autenticação e autorização via JWT (OAuth2)

- Proteção de rotas com Depends()

- Migrações versionadas com Alembic

- Boas práticas RESTful e docstrings detalhadas
