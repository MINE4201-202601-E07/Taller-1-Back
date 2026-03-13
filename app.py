from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from database.connection import engine, Base, get_db
from modules.users.user_movie_preference_service import UserMoviePreferenceService
from modules.users.user_movie_preference_model import UserMoviePreference
from modules.users.user_service import UserService
from modules.users.user_model import User
from modules.movies.movie_model import Movie

# Conjunto de películas disponibles
MOVIES = [
    {
        "id": "1",
        "name": "The Shawshank Redemption",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "genre": "Drama",
        "rating": 9.3,
        "imdbLink": "https://www.imdb.com/title/tt0111161/",
        "releaseYear": 1994,
        "director": "Frank Darabont"
    },
    {
        "id": "2",
        "name": "The Godfather",
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his youngest son.",
        "genre": "Crime",
        "rating": 9.2,
        "imdbLink": "https://www.imdb.com/title/tt0068646/",
        "releaseYear": 1972,
        "director": "Francis Ford Coppola"
    },
    {
        "id": "3",
        "name": "The Dark Knight",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological risks.",
        "genre": "Action",
        "rating": 9.0,
        "imdbLink": "https://www.imdb.com/title/tt0468569/",
        "releaseYear": 2008,
        "director": "Christopher Nolan"
    },
    {
        "id": "4",
        "name": "Pulp Fiction",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
        "genre": "Crime",
        "rating": 8.9,
        "imdbLink": "https://www.imdb.com/title/tt0110912/",
        "releaseYear": 1994,
        "director": "Quentin Tarantino"
    },
    {
        "id": "5",
        "name": "Forrest Gump",
        "description": "The presidencies of Kennedy and Johnson unfold from the perspective of an Alabama man with an IQ of 75.",
        "genre": "Drama",
        "rating": 8.8,
        "imdbLink": "https://www.imdb.com/title/tt0109830/",
        "releaseYear": 1994,
        "director": "Robert Zemeckis"
    },
    {
        "id": "6",
        "name": "Inception",
        "description": "A skilled thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
        "genre": "Sci-Fi",
        "rating": 8.8,
        "imdbLink": "https://www.imdb.com/title/tt1375666/",
        "releaseYear": 2010,
        "director": "Christopher Nolan"
    },
    {
        "id": "7",
        "name": "The Matrix",
        "description": "A computer programmer discovers that reality as he knows it is a simulation created by machines.",
        "genre": "Sci-Fi",
        "rating": 8.7,
        "imdbLink": "https://www.imdb.com/title/tt0133093/",
        "releaseYear": 1999,
        "director": "Lana Wachowski, Lilly Wachowski"
    },
    {
        "id": "8",
        "name": "Interstellar",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "genre": "Sci-Fi",
        "rating": 8.6,
        "imdbLink": "https://www.imdb.com/title/tt0816692/",
        "releaseYear": 2014,
        "director": "Christopher Nolan"
    }
]

# Base de datos en SQLite (se crea automáticamente)
# USERS dictionary ya no es necesario - usamos SQLAlchemy ORM

app = Flask(__name__)
CORS(app)

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)


def startup():
    """Function that runs once when the application starts"""
    print("✓ Application started successfully!")
    print("✓ Server is running on http://localhost:5000")
    print("✓ Available endpoints:")
    print("  - POST /auth/signup")
    print("  - POST /auth/login")
    print("  - GET /sr_user_user?text=<string>")
    print("  - GET /sr_item_item?text=<string>")
    print("  - GET /resync")
    print("  - GET /health")
    print("  - GET /user/<user_id>/preferences - Obtener todas las preferencias")
    print("  - GET /user/<user_id>/preferences/details - Obtener preferencias con detalles de películas")
    print("  - GET /user/<user_id>/movie/<movie_id>/preference - Obtener preferencia de película")


@app.route('/auth/signup', methods=['POST'])
def signup():
    """Endpoint para registrar un nuevo usuario en SQLite"""
    try:
        data = request.get_json()
        
        # Validación del email
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        email = data.get('email')
        password = data.get('password', '')
        name = data.get('name', '')
        
        # Obtener conexión a la BD
        db = next(get_db())
        
        try:
            # Verificar si el email ya está registrado
            existing_user = db.query(User).filter_by(email=email).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'Email already registered'
                }), 400
            
            # Crear nuevo usuario en la BD
            user = UserService.create_user(db, email, name, password)
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                }
            }), 201
        finally:
            db.close()
        
    except Exception as error:
        print(f"Error in signup: {error}")
        return jsonify({
            'success': False,
            'message': 'Error creating user'
        }), 500


@app.route('/auth/login', methods=['POST'])
def login():
    """Endpoint para autenticar un usuario desde SQLite"""
    try:
        data = request.get_json()
        
        # Validación del ID
        if not data or not data.get('id'):
            return jsonify({
                'success': False,
                'message': 'ID is required'
            }), 400
        
        user_id = data.get('id')
        
        db = next(get_db())
        
        try:
            user = UserService.get_user_by_id(db, user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid ID'
                }), 401
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                }
            }), 200
        finally:
            db.close()
        
    except Exception as error:
        print(f"Error in login: {error}")
        return jsonify({
            'success': False,
            'message': 'Error during login'
        }), 500

@app.route('/user', methods=['GET'])
def get_user():
    """Obtener información de un usuario desde SQLite"""
    user_id = request.args.get('userId', type=int)
    
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'userId is required'
        }), 400
    
    db = next(get_db())
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
    finally:
        db.close()

@app.route('/sr_user_user', methods=['GET'])
def sr_user_user():
    """First endpoint that returns random movies"""
    # TODO
    limit = request.args.get('limit', default=5, type=int)
    movies_subset = random.sample(MOVIES, min(limit, len(MOVIES)))
    return jsonify({'movies': movies_subset})


@app.route('/sr_item_item', methods=['GET'])
def sr_item_item():
    """Second endpoint that returns random movies"""
    # TODO
    limit = request.args.get('limit', default=5, type=int)
    movies_subset = random.sample(MOVIES, min(limit, len(MOVIES)))
    return jsonify({'movies': movies_subset})


@app.route('/resync', methods=['GET'])
def resync():
    return jsonify({'endpoint': 'resync', 'status': 'resynced'})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/user/<user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    print (f"Received request for user_id: {user_id}")
    """
    Endpoint para obtener todas las preferencias de un usuario
    """
    try:
        db = next(get_db())
        try:
            preferences = UserMoviePreferenceService.get_user_preferences(db, int(user_id))
            
            return jsonify({
                'success': True,
                'preferences': [
                    {
                        'id': p.id,
                        'user_id': p.user_id,
                        'movie_id': p.movie_id,
                        'rating': p.rating,
                        'created_at': p.created_at.isoformat() if p.created_at else None,
                        'updated_at': p.updated_at.isoformat() if p.updated_at else None
                    }
                    for p in preferences
                ]
            }), 200
        finally:
            db.close()
        
    except Exception as error:
        print(f"Error in get_user_preferences: {error}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving preferences'
        }), 500


@app.route('/user/<user_id>/preferences/details', methods=['GET'])
def get_user_preferences_with_details(user_id):
    """
    Endpoint para obtener todas las preferencias de un usuario con detalles de las películas
    
    Retorna un JSON con:
    - success: boolean
    - preferences: lista de objetos con:
        - id, user_id, movie_id, rating, created_at, updated_at
        - movie: objeto con title, genres, movie_id
    """
    try:
        db = next(get_db())
        try:
            preferences = UserMoviePreferenceService.get_user_preferences_with_details(db, int(user_id))
            
            return jsonify({
                'success': True,
                'preferences': preferences
            }), 200
        finally:
            db.close()
        
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid user_id format'
        }), 400
    except Exception as error:
        print(f"Error in get_user_preferences_with_details: {error}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving preferences'
        }), 500


@app.route('/user/<user_id>/movie/<movie_id>/preference', methods=['GET'])
def get_movie_preference(user_id, movie_id):
    """
    Endpoint para obtener la preferencia de un usuario para una película específica
    """
    try:
        db = next(get_db())
        try:
            preference = UserMoviePreferenceService.get_preference(db, int(user_id), movie_id)
            
            if not preference:
                return jsonify({
                    'success': False,
                    'message': 'Preference not found'
                }), 404
            
            return jsonify({
                'success': True,
                'preference': {
                    'id': preference.id,
                    'user_id': preference.user_id,
                    'movie_id': preference.movie_id,
                    'rating': preference.rating,
                    'liked': preference.liked,
                    'visited': preference.visited,
                    'created_at': preference.created_at.isoformat() if preference.created_at else None,
                    'updated_at': preference.updated_at.isoformat() if preference.updated_at else None
                }
            }), 200
        finally:
            db.close()
        
    except Exception as error:
        print(f"Error in get_movie_preference: {error}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving preference'
        }), 500

def convert_movie_to_json(movie: Movie):
    """Función para crear un JSON de película a partir de un objeto Movie"""
    # Obtener el primer link de IMDB si existe
    imdb_id = movie.movie_links[0].imdb_id if movie.movie_links else None
    imdb_link = f"https://www.imdb.com/title/tt0{imdb_id}/" if imdb_id else None
    
    return {
        'id': movie.movie_id,
        'name': movie.title,
        'genre': movie.genres,
        'imdbLink': imdb_link
    }


if __name__ == '__main__':
    startup()
    app.run(debug=True, port=5000)