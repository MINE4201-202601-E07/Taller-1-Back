"""
Pruebas unitarias para los endpoints de la API
"""

import pytest
import json
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, get_db
from database.connection import engine, Base
from modules.users.user_model import User
from modules.users.user_movie_preference_model import UserMoviePreference


@pytest.fixture
def db_setup():
    """Fixture que prepara la base de datos para pruebas"""
    # Crear las tablas
    Base.metadata.create_all(bind=engine)
    yield
    # Limpiar después de las pruebas
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_setup):
    """Fixture que proporciona un cliente de prueba"""
    app.config['TESTING'] = True
    
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def sample_user(db_setup):
    """Fixture que crea un usuario de prueba"""
    import uuid
    db = next(get_db())
    
    # Usar email único para evitar conflictos
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    user = User(
        email=unique_email,
        name="Test User",
        password="hashed_password_123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user
    
    # Limpiar después del test
    db.delete(user)
    db.commit()


@pytest.fixture
def sample_preferences(sample_user, db_setup):
    """Fixture que crea preferencias de prueba para un usuario"""
    db = next(get_db())
    
    preferences = [
        UserMoviePreference(
            user_id=sample_user.id,
            movie_id="1",
            rating=5
        ),
        UserMoviePreference(
            user_id=sample_user.id,
            movie_id="2",
            rating=4
        ),
        UserMoviePreference(
            user_id=sample_user.id,
            movie_id="3",
            rating=3
        ),
    ]
    
    for pref in preferences:
        db.add(pref)
    
    db.commit()
    
    yield preferences
    
    # Limpiar después del test
    for pref in preferences:
        db.delete(pref)
    db.commit()


class TestUserPreferencesEndpoint:
    """Pruebas para el endpoint GET /user/<user_id>/preferences"""
    
    def test_get_user_preferences_success(self, client, sample_user, sample_preferences):
        """
        Test: Obtener las preferencias de un usuario existente
        Resultado esperado: Status 200 con las 3 preferencias
        """
        response = client.get(f'/user/{sample_user.id}/preferences')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert len(data['preferences']) == 3
        
        # Verificar que contiene los datos esperados
        preferences = data['preferences']
        assert preferences[0]['movie_id'] == "1"
        assert preferences[0]['rating'] == 5
        assert preferences[1]['movie_id'] == "2"
        assert preferences[1]['rating'] == 4
        assert preferences[2]['movie_id'] == "3"
        assert preferences[2]['rating'] == 3
    
    def test_get_user_preferences_empty(self, client, sample_user):
        """
        Test: Obtener preferencias de un usuario sin preferencias
        Resultado esperado: Status 200 con lista vacía
        """
        response = client.get(f'/user/{sample_user.id}/preferences')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert len(data['preferences']) == 0
    
    def test_get_user_preferences_invalid_user(self, client):
        """
        Test: Obtener preferencias de un usuario inexistente
        Resultado esperado: Status 200 con lista vacía
        """
        response = client.get('/user/99999/preferences')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert len(data['preferences']) == 0
    
    def test_get_user_preferences_invalid_user_id(self, client):
        """
        Test: Obtener preferencias con user_id inválido (no es número)
        Resultado esperado: Status 500 con error
        """
        response = client.get('/user/invalid_id/preferences')
        
        # El endpoint devuelve 500 porque int() falla al intentar convertir
        assert response.status_code == 500


class TestUserPreferencesStructure:
    """Pruebas sobre la estructura de las preferencias retornadas"""
    
    def test_preference_object_structure(self, client, sample_user, sample_preferences):
        """
        Test: Verificar que cada preferencia tenga la estructura correcta
        Campos esperados: id, user_id, movie_id, rating, created_at, updated_at
        """
        response = client.get(f'/user/{sample_user.id}/preferences')
        data = json.loads(response.data)
        
        preference = data['preferences'][0]
        
        # Verificar que contiene todos los campos esperados
        assert 'id' in preference
        assert 'user_id' in preference
        assert 'movie_id' in preference
        assert 'rating' in preference
        assert 'created_at' in preference
        assert 'updated_at' in preference
    
    def test_preference_rating_type(self, client, sample_user, sample_preferences):
        """
        Test: Verificar que el rating es un número
        """
        response = client.get(f'/user/{sample_user.id}/preferences')
        data = json.loads(response.data)
        
        for preference in data['preferences']:
            assert isinstance(preference['rating'], (int, type(None)))
    
    def test_preference_movie_id_type(self, client, sample_user, sample_preferences):
        """
        Test: Verificar que movie_id es string
        """
        response = client.get(f'/user/{sample_user.id}/preferences')
        data = json.loads(response.data)
        
        for preference in data['preferences']:
            assert isinstance(preference['movie_id'], str)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
