from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

from ai_agent_service.core.config import get_settings
from ai_agent_service.db.models import Base


def _ensure_sqlite_parent_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite:///") or database_url == "sqlite:///:memory:":
        return

    sqlite_path = database_url.removeprefix("sqlite:///")
    if sqlite_path and sqlite_path != ":memory:":
        Path(sqlite_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def create_session_factory(database_url: str) -> sessionmaker[SQLAlchemySession]:
    _ensure_sqlite_parent_directory(database_url)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[SQLAlchemySession]:
    return create_session_factory(get_settings().database_url)


def init_database(session_factory: sessionmaker[SQLAlchemySession] | None = None) -> None:
    factory = session_factory or get_session_factory()
    Base.metadata.create_all(bind=factory.kw["bind"])


def get_database_session() -> Generator[SQLAlchemySession, None, None]:
    session_factory = get_session_factory()
    with session_factory() as session:
        yield session
