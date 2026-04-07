# Flask Boilerplate

Skeleton de aplicação Flask production-ready com autenticação, MySQL, migrations e testes.

## Stack

- **Flask 3** — Application Factory + Blueprints
- **SQLAlchemy 2 + Flask-Migrate** — ORM + migrations Alembic
- **Flask-Login** — gerenciamento de sessão
- **Flask-WTF** — formulários com validação e proteção CSRF
- **PyMySQL** — driver MySQL puro-Python
- **Gunicorn** — servidor WSGI para produção
- **pytest** — suíte de testes

## Como rodar

### 1. Clonar / criar diretório

```bash
git clone <repo-url> meu_app
cd meu_app
```

### 2. Criar ambiente virtual

```bash
# Linux / macOS
python -m venv .venv && source .venv/bin/activate

# Windows
python -m venv .venv && .venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements-dev.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com as credenciais do banco MySQL **já existente**:

```
SECRET_KEY=<gere com: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/meu_app?charset=utf8mb4
```

### 5. Banco de dados

**Desenvolvimento** — as tabelas são criadas automaticamente no boot (`AUTO_CREATE_TABLES=True`). Nenhum comando adicional é necessário.

**Produção** — use Flask-Migrate para versionar o schema:

```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### 6. Rodar em desenvolvimento

```bash
flask run
# ou
python run.py
```

Acesse: `http://localhost:5000`

### 7. Rodar testes

```bash
pytest

# Com cobertura
pytest --cov=app --cov-report=term-missing
```

### 8. Rodar em produção

```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## Estrutura

```
app/
├── __init__.py          # create_app() — application factory
├── extensions.py        # db, migrate, login_manager, csrf
├── models/user.py       # Modelo User com Flask-Login
├── routes/
│   ├── main.py          # Blueprint main (/, /dashboard, /about)
│   └── auth.py          # Blueprint auth (/auth/login, /register, /logout)
├── forms/auth_forms.py  # LoginForm, RegisterForm (Flask-WTF)
├── errors/handlers.py   # Handlers globais 403/404/500
├── utils/logger.py      # RotatingFileHandler
└── templates/           # Jinja2 com herança de base.html
config.py                # Config, Development, Testing, Production
run.py                   # Entry point dev
wsgi.py                  # Entry point produção (gunicorn)
```

## Gerar SECRET_KEY segura

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
