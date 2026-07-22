# src/db/

Esquema y conexión a la base de datos MySQL.

- `models.py`: modelos SQLAlchemy declarativos. `Comment` (texto original) y `Prediction` (resultado de clasificación, relacionado 1-a-muchos con `Comment` vía `comment_id`) — separados para poder re-clasificar un mismo comentario con una versión de modelo distinta sin perder el historial.
- `session.py`: arma la URL de conexión a MySQL desde variables de entorno (`.env`, ver `.env.example`) y expone `engine` y `SessionLocal` para abrir sesiones.

La base de datos corre en un contenedor Docker local (ver instrucciones en el `README.md` raíz del proyecto); `scripts/init_db.py` crea las tablas.
