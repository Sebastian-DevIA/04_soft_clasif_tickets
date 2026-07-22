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
