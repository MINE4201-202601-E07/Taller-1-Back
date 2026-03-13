import json
from sqlalchemy.orm import Session
from sqlalchemy import func
from modules.users.user_movie_preference_model import UserMoviePreference
from modules.users.popular_movies_cache_model import PopularMoviesCache
from modules.movies.movie_model import Movie
from modules.movies.movie_link_model import MovieLink

class UserMoviePreferenceService:
    POPULAR_MOVIES_CACHE_KEY = "imdb_weighted_popular_movies_v1"
    POPULAR_MOVIES_CACHE_MAX_ITEMS = 1000

    @staticmethod
    def save_preference(db: Session, user_id: int, movie_id: str, rating: float = None, liked: bool = None, visited: bool = None):
        """
        Guardar o actualizar la preferencia de un usuario para una película
        """
        preference = db.query(UserMoviePreference).filter(
            UserMoviePreference.user_id == user_id,
            UserMoviePreference.movie_id == movie_id
        ).first()
        
        if preference:
            if rating is not None:
                preference.rating = rating
            if liked is not None:
                preference.liked = liked
            if visited is not None:
                preference.visited = visited
            db.commit()
        else:
            preference = UserMoviePreference(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating,
                liked=liked,
                visited=visited
            )
            db.add(preference)
            db.commit()

        db.refresh(preference)
        return preference

    @staticmethod
    def get_user_preferences(db: Session, user_id: int):
        """Obtener todas las preferencias de un usuario"""
        return db.query(UserMoviePreference).filter(
            UserMoviePreference.user_id == user_id
        ).all()

    @staticmethod
    def get_preference(db: Session, user_id: int, movie_id: str):
        """Obtener la preferencia de un usuario para una película específica"""
        return db.query(UserMoviePreference).filter(
            UserMoviePreference.user_id == user_id,
            UserMoviePreference.movie_id == movie_id
        ).first()
        
    @staticmethod
    def delete_preference(db: Session, user_id: int, movie_id: str):
        """Eliminar la preferencia de un usuario para una película"""
        preference = db.query(UserMoviePreference).filter(
            UserMoviePreference.user_id == user_id,
            UserMoviePreference.movie_id == movie_id
        ).first()
        
        if preference:
            db.delete(preference)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_preferences_with_details(db: Session, user_id: int):
        """
        Obtener todas las preferencias de un usuario con detalles de las películas
        
        Retorna una lista de diccionarios con:
        - id: ID de la preferencia
        - user_id: ID del usuario
        - movie_id: ID de la película
        - rating: Rating otorgado por el usuario
        - created_at: Fecha de creación
        - updated_at: Última fecha de actualización
        - movie: Objeto con detalles de la película (title, genres, movie_id)
        """
        preferences = db.query(UserMoviePreference).filter(
            UserMoviePreference.user_id == user_id
        ).all()
        
        result = []
        for pref in preferences:
            # Obtener los detalles de la película
            movie = db.query(Movie).filter(
                Movie.movie_id == int(pref.movie_id)
            ).first()
            
            pref_dict = {
                'id': pref.id,
                'user_id': pref.user_id,
                'movie_id': pref.movie_id,
                'rating': pref.rating,
                'created_at': pref.created_at.isoformat() if pref.created_at else None,
                'updated_at': pref.updated_at.isoformat() if pref.updated_at else None,
                'movie': {
                    'movie_id': movie.movie_id,
                    'title': movie.title,
                    'genres': movie.genres
                } if movie else None
            }
            result.append(pref_dict)
        
        return result


    @staticmethod
    def get_most_popular_movies(db: Session, n: int, force_refresh: bool = False):
        """
        Obtener las n películas más populares desde la tabla cacheada.
        Solo recalcula si se fuerza explícitamente o si no existe cache.
        """
        if n <= 0:
            return []

        UserMoviePreferenceService.ensure_popular_movies_cache(
            db,
            max_items=max(n, UserMoviePreferenceService.POPULAR_MOVIES_CACHE_MAX_ITEMS),
            force_refresh=force_refresh
        )

        cached = db.query(PopularMoviesCache).filter(
            PopularMoviesCache.cache_key == UserMoviePreferenceService.POPULAR_MOVIES_CACHE_KEY
        ).first()
        if not cached:
            return []

        return json.loads(cached.payload)[:n]

    @staticmethod
    def ensure_popular_movies_cache(db: Session, max_items: int = None, force_refresh: bool = False):
        """
        Inicializa cache de populares una sola vez por arranque.
        Si ya existe en tabla, no recalcula.
        """
        if max_items is None or max_items <= 0:
            max_items = UserMoviePreferenceService.POPULAR_MOVIES_CACHE_MAX_ITEMS

        cached = db.query(PopularMoviesCache).filter(
            PopularMoviesCache.cache_key == UserMoviePreferenceService.POPULAR_MOVIES_CACHE_KEY
        ).first()

        if (
            cached
            and not force_refresh
            and cached.total_movies > 0
            and bool(cached.payload)
        ):
            return False

        computed_movies = UserMoviePreferenceService._compute_popular_movies(db, limit=max_items)
        UserMoviePreferenceService._upsert_popular_movies_cache(db, computed_movies)
        return True

    @staticmethod
    def _upsert_popular_movies_cache(db: Session, movies: list):
        payload = json.dumps(movies)
        cache = db.query(PopularMoviesCache).filter(
            PopularMoviesCache.cache_key == UserMoviePreferenceService.POPULAR_MOVIES_CACHE_KEY
        ).first()

        if cache:
            cache.payload = payload
            cache.total_movies = len(movies)
        else:
            cache = PopularMoviesCache(
                cache_key=UserMoviePreferenceService.POPULAR_MOVIES_CACHE_KEY,
                payload=payload,
                total_movies=len(movies)
            )
            db.add(cache)

        db.commit()

    @staticmethod
    def _compute_popular_movies(db: Session, limit: int):
        """
        Cálculo pesado del ranking de popularidad (método IMDb).
        Se ejecuta al refrescar el cache, no en cada request.
        """
        # IMDb weighted rating formula:
        # WR = (v/(v+m)) * R + (m/(v+m)) * C
        # v = number of votes for the movie
        # m = minimum votes required to be listed (here, median of votes)
        # R = average rating for the movie
        # C = mean rating across all movies

        # Calculate C (mean rating across all movies)
        C = db.query(func.avg(UserMoviePreference.rating)).filter(UserMoviePreference.rating != None).scalar()
        if C is None:
            return []

        # Calculate v for each movie and R (average rating per movie)
        movie_stats = db.query(
            UserMoviePreference.movie_id,
            func.count(UserMoviePreference.rating).label('v'),
            func.avg(UserMoviePreference.rating).label('R')
        ).filter(UserMoviePreference.rating != None).group_by(UserMoviePreference.movie_id).all()
        if not movie_stats:
            return []

        # Calculate m (median of votes)
        votes = [stat.v for stat in movie_stats]
        m = int(sorted(votes)[len(votes)//2]) if votes else 0

        # Calculate weighted rating for each movie
        weighted_movies = []
        for stat in movie_stats:
            v = stat.v
            R = stat.R
            movie_id = stat.movie_id
            if m == 0:
                WR = R
            else:
                WR = (v / (v + m)) * R + (m / (v + m)) * C
            weighted_movies.append((movie_id, WR, v, R))

        # Sort by weighted rating descending and return top n
        weighted_movies.sort(key=lambda x: x[1], reverse=True)
        top_movies = weighted_movies[:limit]

        movie_ids = [int(movie_id) for movie_id, _, _, _ in top_movies]
        movies = db.query(Movie).filter(Movie.movie_id.in_(movie_ids)).all() if movie_ids else []
        movies_by_id = {movie.movie_id: movie for movie in movies}
        imdb_rows = db.query(
            MovieLink.movie_id,
            func.min(MovieLink.imdb_id).label('imdb_id')
        ).filter(
            MovieLink.movie_id.in_(movie_ids)
        ).group_by(MovieLink.movie_id).all() if movie_ids else []
        imdb_by_movie_id = {row.movie_id: row.imdb_id for row in imdb_rows}

        # Fetch movie details
        result = []
        for movie_id, WR, v, R in top_movies:
            movie = movies_by_id.get(int(movie_id))
            if movie:
                imdb_id = imdb_by_movie_id.get(int(movie_id))
                imdb_link = (
                    f"https://www.imdb.com/title/tt{str(imdb_id).zfill(7)}/"
                    if imdb_id
                    else None
                )
                result.append({
                    'movie_id': movie.movie_id,
                    'title': movie.title,
                    'imdbLink': imdb_link,
                    'genres': movie.genres,
                    'weighted_rating': float(WR),
                    'votes': int(v),
                    'average_rating': float(R)
                })
        return result