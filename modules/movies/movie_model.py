from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connection import Base


class Movie(Base):
    __tablename__ = "movie"

    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False, index=True)
    genres = Column(String(50), nullable=True)

    # Relación con MovieLink (uno a muchos)
    movie_links = relationship("MovieLink", back_populates="movie", cascade="all, delete-orphan")


