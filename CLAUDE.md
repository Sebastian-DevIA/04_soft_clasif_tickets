# CLAUDE.md — contexto del proyecto 04_soft_clasif_tickets

## Qué es este proyecto

Clasificador de comentarios/reseñas de clientes por sentimiento (NLP), con persistencia en MySQL y API REST. Es un proyecto de portafolio construido específicamente para cubrir los conocimientos de NLP y MySQL que piden vacantes junior de Python/ML, complementando el proyecto de conteo vehicular (`03_soft_detec_aforo`), que cubre visión por computadora. El usuario está aprendiendo a programar full-stack construyendo proyectos reales; las sesiones priorizan explicar el porqué de cada pieza, no solo entregar código.

## Decisiones de arquitectura tomadas (no reabrir sin justificación)

- **NLP**: scikit-learn (TF-IDF + clasificador clásico como Naive Bayes o Logistic Regression) + spaCy para preprocesamiento. No se usan transformers/LLMs pesados: la vacante objetivo pide NLP "básico-intermedio", así que el modelo clásico es la elección correcta y honesta para el nivel del puesto.
- **Base de datos**: MySQL (vía SQLAlchemy + PyMySQL), a propósito distinto de SQLite usado en `03_soft_detec_aforo`, porque la vacante pide MySQL específicamente.
- **Backend**: FastAPI + Pydantic v2, mismo estándar que el otro proyecto.
- **Datos de entrenamiento**: dataset público ya etiquetado (reseñas/comentarios en español), no etiquetado manualmente — se prioriza avanzar rápido al modelado.
- **Alcance del MVP**: clasificación de **sentimiento** únicamente. Clasificación adicional por tema/urgencia queda como extensión post-MVP.

## Esquema de base de datos (referencia, sujeto a definirse en Hito 4)

- `comments (id, text, source, created_at)`
- `predictions (id, comment_id, sentiment, confidence, model_version, predicted_at)`

## Convenciones de trabajo

- Cada pieza nueva de código se explica antes de escribirse (analogía + por qué importa para el negocio real).
- No se avanza de un hito al siguiente sin pasar su verificación.
- Al cerrar cada sesión de trabajo se registra en `docs/DECISIONES.md` qué se construyó y qué decisión técnica se tomó.
- Se trabaja en modo **agent teams**: `tech-lead` orquesta y delega en `backend-fastapi`, `devops-git`, `qa-tester`, `security-auditor` según el hito.
- Flujo de ramas: `dev` para desarrollo, `main` solo recibe merges desde `dev` una vez verificado un hito. Nunca se commitea directo a `main`.

## Repositorio

Remoto en GitHub (cuenta Sebastian-DevIA): `git@github-sebastiandevia:Sebastian-DevIA/04_soft_clasif_tickets.git` (mismo alias SSH configurado para `03_soft_detec_aforo`).
