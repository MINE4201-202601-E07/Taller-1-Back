from sqlalchemy.orm import Session
from sqlalchemy import func
from modules.users.user_movie_preference_model import UserMoviePreference
from modules.movies.movie_model import Movie

class UserMoviePreferenceService:
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
