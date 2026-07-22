# scripts/

Scripts ejecutables, uno por etapa del pipeline (correr con la venv activada, desde la raíz del proyecto):

- `explore_dataset.py`: descarga/carga el dataset y muestra forma, nulos, balance de clases y longitud de texto.
- `train_model.py`: entrena el clasificador de sentimiento, imprime el reporte de evaluación y guarda el modelo en `models/`.
- `init_db.py`: crea las tablas de MySQL (`comments`, `predictions`) a partir de `src/db/models.py`.
