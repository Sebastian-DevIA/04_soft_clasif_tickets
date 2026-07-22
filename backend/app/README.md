# backend/app/

API REST en FastAPI, separada en capas:

- `main.py`: instancia la app, monta el router de comentarios bajo `/api`, expone `GET /health`.
- `api/routes/comments.py`: solo orquesta — recibe la request, llama al service correspondiente, traduce errores a `HTTPException` con mensajes claros (nunca un traceback crudo al cliente). Endpoints: `POST /api/comments`, `GET /api/comments` (filtros `sentiment`, `limit`, `offset`), `GET /api/comments/{id}`.
- `services/classification.py`: carga el modelo entrenado una sola vez (singleton a nivel de módulo) y expone `classify_text()`.
- `services/comments.py`: toda la lógica de negocio — clasificar + persistir `Comment`+`Prediction` en una sola transacción, listar con filtros, obtener por id. Reutilizable desde scripts o tests sin depender de FastAPI.
- `schemas/comments.py`: contratos Pydantic de entrada/salida (`CommentIn`, `CommentOut`, `PredictionOut`).
- `dependencies.py`: `get_db()` — abre una sesión de SQLAlchemy por request y la cierra siempre en `finally`.

Correr localmente (con la venv activada, MySQL en Docker corriendo y el modelo ya entrenado):

```bash
uvicorn backend.app.main:app --reload
```

Luego abrir `http://127.0.0.1:8000/docs` para probar los endpoints.
