"""Suite de pruebas de la API del clasificador de sentimiento.

Cubre: happy path de creacion + clasificacion, persistencia real en MySQL,
paginacion/filtros de listado, 404 en id inexistente, manejo de errores
internos (nunca traceback crudo) y validacion de texto vacio.
"""

from unittest.mock import patch

from src.db.models import Comment, Prediction

POSITIVE_TEXT = "me encanta este producto, es excelente"


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /api/comments - camino feliz
# ---------------------------------------------------------------------------


def test_create_comment_positive_happy_path(client):
    response = client.post("/api/comments", json={"text": POSITIVE_TEXT})

    assert response.status_code == 201
    body = response.json()
    assert body["text"] == POSITIVE_TEXT
    assert body["source"] == "api"  # default aplicado

    prediction = body["prediction"]
    assert prediction is not None
    assert prediction["sentiment"] == "positive"
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert prediction["model_version"]


def test_create_comment_default_source_is_api(client):
    response = client.post("/api/comments", json={"text": "un comentario sin source explicito"})

    assert response.status_code == 201
    assert response.json()["source"] == "api"


def test_create_comment_custom_source_is_respected(client):
    response = client.post(
        "/api/comments", json={"text": "comentario desde otro canal", "source": "whatsapp"}
    )

    assert response.status_code == 201
    assert response.json()["source"] == "whatsapp"


# ---------------------------------------------------------------------------
# Persistencia real en MySQL
# ---------------------------------------------------------------------------


def test_created_comment_is_persisted_in_mysql(client, db_session):
    response = client.post(
        "/api/comments", json={"text": POSITIVE_TEXT, "source": "qa-test"}
    )
    assert response.status_code == 201
    comment_id = response.json()["id"]

    # Verificacion directa contra MySQL, sin pasar por la API.
    row = db_session.get(Comment, comment_id)
    assert row is not None
    assert row.text == POSITIVE_TEXT
    assert row.source == "qa-test"

    prediction_row = (
        db_session.query(Prediction).filter(Prediction.comment_id == comment_id).one()
    )
    assert prediction_row.sentiment == "positive"
    assert prediction_row.confidence > 0.0

    # Y tambien vale re-consultarlo por la propia API.
    get_response = client.get(f"/api/comments/{comment_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == comment_id


# ---------------------------------------------------------------------------
# GET /api/comments - listado, paginacion y filtros
# ---------------------------------------------------------------------------


def test_list_comments_respects_limit(client):
    # Nos aseguramos de que existan al menos dos filas antes de pedir limit=1.
    client.post("/api/comments", json={"text": "otro comentario cualquiera"})
    client.post("/api/comments", json={"text": "y otro mas para tener varias filas"})

    response = client.get("/api/comments", params={"limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert len(body) <= 1


def test_list_comments_filter_by_sentiment(client):
    created = client.post("/api/comments", json={"text": POSITIVE_TEXT}).json()
    target_sentiment = created["prediction"]["sentiment"]

    response = client.get(
        "/api/comments", params={"sentiment": target_sentiment, "limit": 100}
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert all(item["prediction"]["sentiment"] == target_sentiment for item in body)
    assert any(item["id"] == created["id"] for item in body)


def test_list_comments_unknown_sentiment_returns_empty_list(client):
    response = client.get(
        "/api/comments", params={"sentiment": "esto-no-es-un-sentimiento-valido"}
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_comments_limit_out_of_range_is_rejected(client):
    assert client.get("/api/comments", params={"limit": 0}).status_code == 422
    assert client.get("/api/comments", params={"limit": 101}).status_code == 422


def test_list_comments_negative_offset_is_rejected(client):
    assert client.get("/api/comments", params={"offset": -1}).status_code == 422


# ---------------------------------------------------------------------------
# GET /api/comments/{id} - 404 legible
# ---------------------------------------------------------------------------


def test_get_comment_not_found_returns_404_with_readable_detail(client):
    response = client.get("/api/comments/999999999")

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], str)
    assert "999999999" in body["detail"]


# ---------------------------------------------------------------------------
# Error interno del clasificador - nunca traceback crudo
# ---------------------------------------------------------------------------


def test_create_comment_classifier_failure_returns_500_without_traceback(client):
    with patch(
        "backend.app.services.comments.classify_text",
        side_effect=RuntimeError("modelo caido"),
    ):
        response = client.post("/api/comments", json={"text": "cualquier texto"})

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body
    detail = body["detail"]
    assert isinstance(detail, str)
    # No debe filtrarse un traceback crudo de Python en el body de la respuesta.
    assert "Traceback" not in detail
    assert 'File "' not in detail


# ---------------------------------------------------------------------------
# Validacion de texto vacio (fix aplicado: CommentIn.text con min_length=1)
# ---------------------------------------------------------------------------


def test_create_comment_with_empty_text_is_rejected_with_422(client):
    response = client.post("/api/comments", json={"text": ""})

    assert response.status_code == 422


def test_create_comment_with_text_over_max_length_is_rejected_with_422(client):
    response = client.post("/api/comments", json={"text": "a" * 5001})

    assert response.status_code == 422
