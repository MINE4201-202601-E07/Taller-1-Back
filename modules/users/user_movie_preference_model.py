from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from datetime import datetime
from database.connection import Base

class UserMoviePreference(Base):
    __tablename__ = "user_movie_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    movie_id = Column(String, index=True)
    rating = Column(Integer, nullable=True)  # Puntuación del usuario (1-5)
    liked = Column(Integer, nullable=True)  # 1 para like, 0 para dislike, None sin decisión
    visited = Column(Boolean, nullable=True, default=False)  # True si el usuario vio la película
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
