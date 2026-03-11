from sqlalchemy.orm import Session
from modules.users.user_movie_preference_model import UserMoviePreference

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
