from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
if settings.database_url.startswith("sqlite"):
    sqlite_path = Path(make_url(settings.database_url).database)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialize_database() -> None:
    from alembic import command
    from alembic.config import Config

    alembic_config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    alembic_config = Config(str(alembic_config_path))
    backend_dir = alembic_config_path.parent
    alembic_config.set_main_option("script_location", str(backend_dir / "migrations"))
    alembic_config.set_main_option("prepend_sys_path", str(backend_dir))
    command.upgrade(alembic_config, "head")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
