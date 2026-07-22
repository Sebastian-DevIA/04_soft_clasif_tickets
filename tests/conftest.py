"""Fixtures compartidas para la suite de tests de la API.

Nota importante sobre la base de datos usada en estos tests: este proyecto
no tiene (todavia) una base de datos de test separada. Por decision explicita
del equipo para el alcance del MVP, los tests corren contra la misma MySQL de
desarrollo (contenedor Docker `clasif_tickets_mysql`) usando `get_db()` tal
cual esta definido en `backend/app/dependencies.py`, sin overrides ni SQLite
en memoria. Esto significa que cada corrida de la suite inserta filas reales
en `comments`/`predictions`. Es un trade-off aceptado para este MVP; si el
proyecto crece, la siguiente mejora natural es una base de datos de test
dedicada (o SQLite + StaticPool) para no ensuciar la DB de desarrollo.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from src.db.session import SessionLocal


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
