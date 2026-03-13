from flask import Flask, request, jsonify
from flask_cors import CORS
from database.connection import engine, Base, get_db
from modules.users.user_movie_preference_service import UserMoviePreferenceService
from modules.users.user_service import UserService
from modules.users.user_model import User
from modules.movies.movie_model import Movie

app = Flask(__name__)
CORS(app)

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)


def startup():
    """Function that runs once when the application starts"""
    db = next(get_db())
    try:
        recalculated = UserMoviePreferenceService.ensure_popular_movies_cache(db)
    finally:
        db.close()

    print("✓ Application started successfully!")
    print("✓ Server is running on http://localhost:5000")
    if recalculated:
        print("✓ Popular movies cache initialized on startup")
    else:
        print("✓ Popular movies cache already exists (startup skipped recalculation)")


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

@app.route('/cold_start/<n>', methods=['GET'])
def cold_start(n):
    """Returns most popular movies"""
    try:
        db = next(get_db())
        try:
            num_movies = int(n)
            force_refresh = request.args.get('refresh', '').lower() in {'1', 'true', 'yes'}
            movies = UserMoviePreferenceService.get_most_popular_movies(
                db,
                num_movies,
                force_refresh=force_refresh
            )
            movies_json = [convert_movie_to_json(movie) for movie in movies]
            return jsonify({'success': True, 'movies': movies_json}), 200
        finally:
            db.close()
    except Exception as error:
        print(f"Error in cold_start: {error}")
        return jsonify({'success': False, 'message': 'Error retrieving popular movies'}), 500


@app.route('/sr_user_user', methods=['GET'])
def sr_user_user():
    # TODO

    return jsonify({'movies': []})

@app.route('/sr_item_item', methods=['GET'])
def sr_item_item():
    # TODO

    return jsonify({'movies': []})


@app.route('/resync', methods=['GET'])
def resync():
    db = next(get_db())
    try:
        max_items = request.args.get('max_items', default=200, type=int)
        cached_movies = UserMoviePreferenceService.get_most_popular_movies(
            db,
            max_items,
            force_refresh=True
        )
        return jsonify({
            'endpoint': 'resync',
            'status': 'resynced',
            'popular_movies_cached': len(cached_movies)
        })
    finally:
        db.close()


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

def convert_movie_to_json(movie):
    """Crear JSON de película desde dict cacheado o desde objeto ORM Movie."""
    if isinstance(movie, dict):
        return {
            'id': movie.get('movie_id'),
            'name': movie.get('title'),
            'genre': movie.get('genres'),
            'imdbLink': movie.get('imdbLink')
        }

    imdb_id = movie.movie_links[0].imdb_id if movie.movie_links else None
    imdb_link = f"https://www.imdb.com/title/tt{str(imdb_id).zfill(7)}/" if imdb_id else None

    return {
        'id': movie.movie_id,
        'name': movie.title,
        'genre': movie.genres,
        'imdbLink': imdb_link
    }


if __name__ == '__main__':
    startup()
    app.run(debug=True, port=5000)