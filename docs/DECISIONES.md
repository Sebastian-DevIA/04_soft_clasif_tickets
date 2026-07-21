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
