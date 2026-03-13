# Pruebas Unitarias - Taller 1 Backend

## Overview

Este proyecto incluye un suite de pruebas unitarias para validar los endpoints del backend. Las pruebas utilizan **pytest** para el framework de testing y **Flask's test client** para simular peticiones HTTP.

## Requisitos

- Python 3.8+
- pytest (ya instalado: `pip install pytest`)
- Las dependencias del proyecto (ver `requirements.txt`)

## Ejecución de las Pruebas

### Ejecutar todas las pruebas
```bash
source .venv/bin/activate  # Activar entorno virtual
pytest test_app.py -v      # Ejecutar con verbose
```

### Ejecutar pruebas de una clase específica
```bash
pytest test_app.py::TestUserPreferencesEndpoint -v
```

### Ejecutar una prueba específica
```bash
pytest test_app.py::TestUserPreferencesEndpoint::test_get_user_preferences_success -v
```

### Ver reportes detallados
```bash
pytest test_app.py -v --tb=short  # Traceback corto
pytest test_app.py -v --tb=long   # Traceback detallado
```

### Generar reporte de coverage (cobertura de código)
```bash
pip install pytest-cov
pytest test_app.py --cov=app --cov-report=html
# Abre htmlcov/index.html en el navegador
```

## Estructura de Pruebas

### Clase: `TestUserPreferencesEndpoint`
Pruebas para el endpoint **GET /user/<user_id>/preferences**

| Prueba | Descripción | Resultado Esperado |
|--------|-------------|-------------------|
| `test_get_user_preferences_success` | Obtener preferencias de usuario con datos | Status 200, 3 preferencias |
| `test_get_user_preferences_empty` | Obtener preferencias de usuario sin datos | Status 200, lista vacía |
| `test_get_user_preferences_invalid_user` | Obtener preferencias de usuario inexistente | Status 200, lista vacía |
| `test_get_user_preferences_invalid_user_id` | User ID no es número | Status 500 (error) |

### Clase: `TestUserPreferencesStructure`
Pruebas sobre la estructura de objetos retornados

| Prueba | Descripción | Validación |
|--------|-------------|-----------|
| `test_preference_object_structure` | Estructura del objeto preferencia | Tiene todos los campos requeridos |
| `test_preference_rating_type` | Tipo de dato del rating | Es Integer o None |
| `test_preference_movie_id_type` | Tipo de dato del movie_id | Es String |

## Fixtures (Datos de Prueba)

Las pruebas utilizan fixtures de pytest para proporcionar datos:

- **`db_setup`**: Crea y limpia las tablas de base de datos
- **`client`**: Cliente HTTP para hacer peticiones a la API
- **`sample_user`**: Usuario de prueba con email único
- **`sample_preferences`**: 3 preferencias asociadas al usuario

## Ejemplo de Resultado

```
===================== test session starts ======================
platform darwin -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0

collected 7 items

test_app.py::TestUserPreferencesEndpoint::test_get_user_preferences_success PASSED [ 14%]
test_app.py::TestUserPreferencesEndpoint::test_get_user_preferences_empty PASSED [ 28%]
test_app.py::TestUserPreferencesEndpoint::test_get_user_preferences_invalid_user PASSED [ 42%]
test_app.py::TestUserPreferencesEndpoint::test_get_user_preferences_invalid_user_id PASSED [ 57%]
test_app.py::TestUserPreferencesStructure::test_preference_object_structure PASSED [ 71%]
test_app.py::TestUserPreferencesStructure::test_preference_rating_type PASSED [ 85%]
test_app.py::TestUserPreferencesStructure::test_preference_movie_id_type PASSED [100%]

======================== 7 passed in 0.15s ==========================
```

## Notas Importantes

- Las pruebas **limpian la base de datos** después de ejecutarse, no afectan la BD principal
- Cada test es **independiente** (no hay dependencias entre ellos)
- Se usan **emails únicos** para evitar conflictos de UNIQUE constraint
- El código **es idempotente**: puedes ejecutar varias veces sin problemas

## Agregar Nuevas Pruebas

Para agregar más pruebas, crea métodos en las clases existentes o nuevas clases:

```python
def test_nuevo_caso(self, client, sample_user):
    """
    Test: Descripción de qué se prueba
    Resultado esperado: Qué se espera que suceda
    """
    response = client.get('/user/...')
    
    assert response.status_code == 200
    # ... más assertions ...
```

## Troubleshooting

### Error: "UNIQUE constraint failed: users.email"
Usa fixtures que generen emails únicos (ya está implementado).

### Error: "sqlite3.OperationalError: no such table"
Asegúrate de que `db_setup` fixture esté siendo usado.

### Tests tardan mucho
Es normal para pruebas de BD. Usa `-x` para parar en el primer error:
```bash
pytest test_app.py -x
```

---

**Última actualización:** 12 de marzo de 2026
