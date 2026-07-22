# data/

- `raw/`: el dataset público descargado sin modificar, cacheado como CSV por `src/data/loader.py` para no depender de internet en cada ejecución. No versionado (solo `.gitkeep`); se regenera corriendo `scripts/explore_dataset.py` o `scripts/train_model.py`.
- `processed/`: reservado para datos limpios/transformados que se quieran persistir en disco (por ahora el preprocesamiento ocurre en memoria dentro del pipeline de scikit-learn, así que esta carpeta está vacía).
