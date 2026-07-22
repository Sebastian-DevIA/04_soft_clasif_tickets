# Bitácora de decisiones técnicas

Registro de qué se construyó y por qué, hito a hito.

## 2026-07-21 — Hito 0: estructura inicial del proyecto

- Proyecto creado para cubrir explícitamente los conocimientos de NLP y MySQL que piden vacantes junior de Python/ML (no cubiertos por `03_soft_detec_aforo`, que es visión por computadora).
- **Decisión**: scikit-learn + spaCy para NLP clásico, no transformers/LLMs. Razón: el perfil de vacante objetivo pide NLP "básico-intermedio"; un modelo clásico bien explicado demuestra el nivel correcto sin sobre-ingeniería.
- **Decisión**: MySQL (no SQLite), a propósito distinto del otro proyecto, porque la vacante pide MySQL específicamente.
- **Decisión**: dataset público ya etiquetado para entrenar, en vez de etiquetado manual, para avanzar rápido al modelado.
- Licencia del repo: MIT.

## 2026-07-21 — Hito 1: adquisición y exploración del dataset

- **Decisión**: dataset elegido: `cardiffnlp/tweet_sentiment_multilingual` (split en español), vía Hugging Face `datasets`. Contiene tweets reales en español clasificados en 3 clases (negative/neutral/positive) — buen sustituto de "comentarios de clientes" cortos e informales.
- Nota técnica: la librería `datasets` ya no soporta datasets con "loading script" (varios candidatos fallaron por eso); hubo que apuntar directo a los archivos parquet de la rama `refs/convert/parquet` del repo en Hugging Face.
- El dataset se descarga una sola vez y se cachea en `data/raw/tweet_sentiment_es.csv` (no se vuelve a descargar en cada ejecución).
- Exploración (`scripts/explore_dataset.py`): 3033 filas totales, sin valores nulos, clases perfectamente balanceadas (613/613/613 en train), longitud de texto entre 19 y 138 caracteres (típico de tweets). No se necesita balanceo de clases para el modelo del Hito 3.

## 2026-07-21 — Hito 2-3: preprocesamiento y entrenamiento del clasificador

- **Bug encontrado y corregido**: la lista de stopwords en español de spaCy incluye negaciones ("no", "nada", "nunca", "ni", "sin", "tampoco") — quitarlas destruye la señal de sentimiento ("no me gusta" se queda en "gusta"). Se excluyen explícitamente de `SPANISH_STOPWORDS` en `src/nlp/preprocess.py`.
- **Decisión**: TF-IDF (unigramas+bigramas) + Logistic Regression como modelo base. Se comparó contra MultinomialNB (baseline clásico para texto disperso): resultado prácticamente idéntico (48% vs 47% accuracy), así que la elección del algoritmo no es el cuello de botella — se mantiene Logistic Regression por dar probabilidades bien calibradas (`predict_proba`), útiles para el campo `confidence` que se guardará en la base de datos.
- **Resultado honesto**: ~47-48% de accuracy sobre 3 clases (el azar sería ~33%). Es un resultado modesto pero realista: la dificultad real viene del dataset (tweets cortos, informales, con ironía/sarcasmo — un desafío bien documentado en la literatura de sentiment analysis), no de un error de implementación. Para el nivel de vacante objetivo (NLP básico-intermedio) esto es honesto y suficiente; no se persigue una mejora artificial con modelos más pesados (transformers) que estarían fuera de alcance del MVP.
- Ideas documentadas para una futura mejora (no implementadas en el MVP): dataset más grande, lematización con spaCy antes de vectorizar, o un modelo de embeddings preentrenado en español.

## 2026-07-21 — Hito 4: base de datos MySQL

- **Decisión**: MySQL corre en un contenedor Docker (`clasif_tickets_mysql`, puerto local 3307 para no chocar con un MySQL nativo en 3306, volumen nombrado `clasif_tickets_mysql_data` para persistencia). Esto hace que cualquiera pueda levantar el proyecto igual, sin instalar MySQL manualmente en su máquina.
- Credenciales en `.env` (gitignorado); `.env.example` documenta las variables requeridas sin exponer secretos reales.
- Esquema: tabla `comments` (texto original) y tabla `predictions` (resultado de la clasificación, con relación 1-a-muchos hacia `comments` vía `comment_id`) — se separan para poder re-clasificar un mismo comentario con una versión de modelo distinta en el futuro sin perder el historial.
- Verificado con `scripts/init_db.py` + consulta directa a MySQL (`DESCRIBE`) confirmando las columnas esperadas.

## 2026-07-21 — Hito 5: backend API (FastAPI)

- **Decisión**: separación estricta en capas dentro de `backend/app/` — `api/routes/` solo orquesta (recibe request, llama al service, valida la respuesta), `services/` concentra toda la lógica de negocio (clasificar + persistir + consultar), `schemas/` define los contratos de entrada/salida. Razón: mantiene los routers finos y testeables, y permite reutilizar los services desde otros entrypoints (scripts, tests) sin arrastrar FastAPI.
- **Decisión**: el modelo de sentimiento se carga UNA sola vez como singleton a nivel de módulo (`backend/app/services/classification.py`), no en cada request. Leer el `.joblib` por petición sería un desperdicio de I/O y CPU; el pipeline es inmutable tras el entrenamiento, así que compartir una instancia es seguro.
- **Decisión**: ciclo de vida de la sesión de DB con `get_db()` (`backend/app/dependencies.py`) que abre `SessionLocal()`, la entrega con `yield` y la cierra siempre en `finally`, inyectada vía `Depends(get_db)`. Una sesión por request, cerrada pase lo que pase.
- **Nota técnica**: `SessionLocal` usa `autoflush=False`, así que al crear un comentario se llama `db.flush()` antes de construir la `Prediction` — necesitamos el `comment.id` autogenerado para la FK. Comentario + predicción se guardan en la misma transacción (`db.commit()` único): o entran ambos o no entra ninguno.
- **Decisión**: `PredictionOut` lleva `protected_namespaces=()` en su `ConfigDict` porque el campo `model_version` colisiona con el namespace reservado `model_` de Pydantic v2 (que si no emite un warning). Se prefirió conservar el nombre `model_version` (coherente con la columna de la tabla) antes que renombrar el campo.
- **Decisión**: los schemas de salida usan `from_attributes=True` y se construyen directamente desde los objetos SQLAlchemy. Como `CommentOut.prediction` es singular pero el modelo expone la relación `predictions` (lista), el service adjunta la última predicción (`max` por `predicted_at`) como atributo `comment.prediction` antes de serializar. Trade-off: es una carga lazy por comentario (N+1) — aceptable para el volumen del MVP; si el listado crece se puede pasar a `selectinload`.
- **Seguridad/robustez**: los errores internos nunca llegan como traceback crudo al cliente — el POST envuelve el fallo del clasificador/persistencia en `HTTPException 500` con mensaje claro, y el GET por id devuelve `404` explícito.
- **Endpoints**: `GET /health`, `POST /api/comments`, `GET /api/comments` (query params `sentiment`, `limit`, `offset`), `GET /api/comments/{id}`.
- **Verificación**: `GET /health` → `{"status":"ok"}`. POST con texto positivo ("me encanta este producto, es excelente") → `positive` (conf. 0.60); POST negativo ("no me gusta nada, pesimo servicio") → `neutral` (conf. 0.55). El negativo no se clasificó como positivo, pero tampoco acertó a `negative`: coherente con la accuracy honesta ~47-48% del modelo (Hito 3), no un bug de la API. Filas confirmadas directamente en MySQL (`comments` y `predictions`, 2 filas cada una, FK correcta).

## 2026-07-21 — Auditoría de seguridad antes del merge a `main`

Auditoría completa (secretos, inyección, manejo de errores, dependencias, OWASP) antes de mergear `dev` a `main` por ser repo público. Veredicto: sin secretos expuestos ni vulnerabilidad crítica; se corrigieron los dos hallazgos de severidad media accionables de inmediato:

- **Fix**: `POST /api/comments` ya no incluye el mensaje crudo de la excepción interna en la respuesta 500 (`backend/app/api/routes/comments.py`) — antes `detail=f"...: {exc}"` podía filtrar nombres de tabla/columna o detalles del driver de MySQL (info disclosure, OWASP API8). Ahora se loguea en servidor (`logger.exception(...)`) y se devuelve un mensaje genérico al cliente.
- **Fix**: `CommentIn` ahora limita `text` a 5000 caracteres y `source` a 50 (igual que la columna `String(50)` del modelo) — antes un texto sin cota podía forzar procesamiento NLP costoso o un error de DB al exceder el tamaño de columna (vector de DoS barato).
- **Nota agregada al README**: advertencia explícita de que la API no tiene autenticación y es un MVP para uso local, no para desplegar en un entorno público tal cual.
- **Backlog documentado, no bloqueante para el MVP**: fijar versiones en `requirements.txt` (hoy usan `>=` sin cota superior) y correr `pip-audit` periódicamente; quitar el fallback silencioso a `root`/sin password en `src/db/session.py` si faltan variables de entorno; considerar `selectinload` en el listado de comentarios si el volumen crece (ya documentado en Hito 5); validar `sentiment` contra un `Literal` en vez de aceptar cualquier string.

## 2026-07-21 — QA: suite de tests de la API (pytest + httpx)

- **Alcance probado** (`tests/test_api.py`, 13 tests, `TestClient` sobre `backend.app.main.app`): `GET /health`; creación de comentario con texto positivo (201, `prediction` no nulo con `sentiment`/`confidence`/`model_version`); `source` por defecto (`"api"`) y `source` explícito; persistencia real en MySQL verificada con consulta directa vía SQLAlchemy (`Comment`/`Prediction`) además de por `GET /api/comments/{id}`; `limit` respetado en el listado; filtro `?sentiment=` (verificado con el sentimiento real que devuelve el modelo, no uno asumido, para no acoplar el test a la accuracy del clasificador) y el caso de un sentimiento inexistente (devuelve lista vacía, no error); `limit`/`offset` fuera de rango → 422; `GET /api/comments/{id}` inexistente → 404 con `detail` legible; fallo simulado del clasificador (`unittest.mock.patch` sobre `classify_text`) → 500 con `detail` de texto plano, nunca un traceback crudo en el body; texto vacío.
- **Bug real encontrado y corregido**: `CommentIn.text` no tenía validación de longitud mínima — un `POST` con `text=""` se aceptaba silenciosamente y el clasificador devolvía una predicción (`positive`, conf. 0.36) sobre una cadena vacía, lo cual no tiene sentido de negocio. Fix aplicado: `text: str = Field(min_length=1)` en `backend/app/schemas/comments.py`. Ahora ese caso devuelve `422`. Test que lo confirma: `test_create_comment_with_empty_text_is_rejected_with_422`.
- **Decisión sobre la base de datos usada en los tests**: no existe (aún) una base de datos de test separada; por decisión explícita para el alcance del MVP, la suite corre contra la misma MySQL de desarrollo (`clasif_tickets_mysql`) usando `get_db()` tal cual, sin overrides ni SQLite en memoria. Cada corrida inserta filas reales en `comments`/`predictions` (verificado: 9 filas en cada tabla tras correr la suite una vez). Riesgo aceptado a propósito para el MVP; la mejora natural a futuro es una DB de test dedicada.
- **Resultado**: `13 passed` en `0.32s`, sin fallos ni tests saltados.
- **Huecos no cubiertos (pendientes, no bloqueantes para este hito)**: no hay tests de concurrencia/carga; no se probó el comportamiento si MySQL está caído (la API no tiene un manejo explícito de `OperationalError` de conexión, solo el catch genérico del POST); no hay tests para `scripts/init_db.py` ni para el pipeline de entrenamiento (`src/nlp/classifier.py`) en sí, solo para su uso vía API; no hay tests de autenticación/autorización porque la API no tiene ese requisito todavía.
- **Actualización post-auditoría de seguridad**: se agregó `max_length` a `text` (5000) y `source` (50) en `CommentIn` — el hueco de "texto extremadamente largo" mencionado arriba quedó cerrado (ver sección de auditoría de seguridad más abajo), con su test correspondiente (`test_create_comment_with_text_over_max_length_is_rejected_with_422`).
