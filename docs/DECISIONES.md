# Bitácora de decisiones técnicas

Registro de qué se construyó y por qué, hito a hito.

## 2026-07-21 — Hito 0: estructura inicial del proyecto

- Proyecto creado para cubrir explícitamente los conocimientos de NLP y MySQL que piden vacantes junior de Python/ML (no cubiertos por `03_soft_detec_aforo`, que es visión por computadora).
- **Decisión**: scikit-learn + spaCy para NLP clásico, no transformers/LLMs. Razón: el perfil de vacante objetivo pide NLP "básico-intermedio"; un modelo clásico bien explicado demuestra el nivel correcto sin sobre-ingeniería.
- **Decisión**: MySQL (no SQLite), a propósito distinto del otro proyecto, porque la vacante pide MySQL específicamente.
- **Decisión**: dataset público ya etiquetado para entrenar, en vez de etiquetado manual, para avanzar rápido al modelado.
- Licencia del repo: MIT.
