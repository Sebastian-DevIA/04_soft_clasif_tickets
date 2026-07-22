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
