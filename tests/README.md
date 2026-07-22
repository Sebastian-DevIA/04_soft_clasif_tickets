# tests/

Pruebas automatizadas de la API con pytest + `fastapi.testclient.TestClient`.

- `conftest.py`: fixtures `client` (TestClient sobre la app real) y `db_session` (sesión directa a MySQL para verificar persistencia sin pasar por la API). Corre contra la misma MySQL de desarrollo — no hay (todavía) una base de datos de test separada; ver la nota en el propio archivo y en `docs/DECISIONES.md`.
- `test_api.py`: happy path de clasificación + persistencia, paginación/filtros de listado, 404 en id inexistente, manejo de errores internos (nunca traceback crudo), y validación de entrada (texto vacío, texto demasiado largo).

Correr la suite (con la venv activada y MySQL en Docker corriendo):

```bash
python -m pytest tests/ -v
```
