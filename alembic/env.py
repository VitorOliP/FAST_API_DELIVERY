from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import sys
import os
from dotenv import load_dotenv

# Carregar .env com DATABASE_URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Objeto de configuração do Alembic
config = context.config

# Corrigir aqui: definir a URL do banco dinamicamente
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configuração de logging (opcional)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar metadados dos modelos
from models import Base
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executar migrações no modo offline"""
    url = config.get_main_option("sqlalchemy.url")  # Corrigido aqui
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executar migrações no modo online"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
