# 04_soft_clasif_tickets

Clasificador de comentarios/reseñas de clientes por sentimiento usando NLP, con persistencia en MySQL y una API REST — pensado como herramienta de analítica para priorizar qué atender primero sin leer todo manualmente.

## ¿Qué hace?

1. Recibe un texto libre (reseña, comentario, ticket de soporte).
2. Lo preprocesa (limpieza, tokenización) y lo clasifica por **sentimiento** (positivo/negativo/neutral) con un modelo de NLP entrenado.
3. Guarda cada texto clasificado en una base de datos MySQL (texto, predicción, confianza, timestamp).
4. Expone los resultados vía una API REST para consultarlos y analizar tendencias.

## Estado actual

Proyecto en construcción, en fase de aprendizaje aplicado. Ver [docs/DECISIONES.md](docs/DECISIONES.md) para el historial de decisiones técnicas tomadas hito a hito.

## Stack

- **NLP**: scikit-learn (TF-IDF + clasificador) y spaCy para preprocesamiento de texto en español.
- **Backend**: FastAPI + SQLAlchemy + Pydantic.
- **Base de datos**: MySQL.
- **Análisis/datos**: pandas, dataset público de reseñas en español.

## Estructura del proyecto

```
04_soft_clasif_tickets/
├── data/               # raw (dataset original) y processed (limpio), no versionados salvo .gitkeep
├── models/             # modelos entrenados serializados (no versionados salvo .gitkeep)
├── src/
│   ├── data/           # carga y exploración del dataset
│   ├── nlp/             # preprocesamiento y clasificador
│   └── db/              # esquema y sesión de base de datos (MySQL)
├── scripts/            # scripts ejecutables: explorar datos, entrenar modelo, inicializar DB
├── backend/app/        # API REST en FastAPI
├── tests/              # pruebas automatizadas (pytest)
└── docs/               # documentación y bitácora de decisiones
```

## Cómo correrlo (en construcción)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

**Base de datos (MySQL vía Docker):**

```bash
docker run -d --name clasif_tickets_mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=clasif_tickets \
  -e MYSQL_USER=clasif_app \
  -e MYSQL_PASSWORD=clasif_app_pass \
  -p 3307:3306 \
  -v clasif_tickets_mysql_data:/var/lib/mysql \
  mysql:8

cp .env.example .env   # ajusta las credenciales si cambiaste algo arriba
python scripts/init_db.py
```

**Entrenar el modelo y correr los scripts:**

```bash
python scripts/explore_dataset.py
python scripts/train_model.py
```

Los pasos concretos de cada etapa se irán documentando aquí a medida que se implementen.

## Roadmap

- [x] Hito 0 — Entorno, estructura del proyecto, documentación base.
- [x] Hito 1 — Adquisición y exploración del dataset público de reseñas (pandas).
- [x] Hito 2 — Preprocesamiento NLP (limpieza, tokenización, TF-IDF).
- [x] Hito 3 — Entrenamiento y evaluación del clasificador de sentimiento.
- [x] Hito 4 — Persistencia en MySQL.
- [x] Hito 5 — Backend API (FastAPI).
- [ ] Hito 6 (post-MVP) — Clasificación adicional por tema/urgencia.
- [ ] Hito 7 (post-MVP) — Dashboard o reporte de tendencias.

## Flujo de trabajo / ramas

Este repositorio usa dos ramas permanentes:

- `dev`: rama de desarrollo, donde se construye cada hito.
- `main`: rama de producción, solo recibe merges desde `dev` cuando un hito está verificado.

## Licencia

Ver [LICENSE.md](LICENSE.md).
