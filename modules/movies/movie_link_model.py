from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class MovieLink(Base):
    __tablename__ = "movie_link"

    movie_id = Column(Integer, ForeignKey("movie.movie_id"), primary_key=True, index=True)
    imdb_id = Column(Integer, primary_key=True, index=True)
    tmdbId = Column(Integer, nullable=True)

    # Relación con Movie (muchos a uno)
    movie = relationship("Movie", back_populates="movie_links")

