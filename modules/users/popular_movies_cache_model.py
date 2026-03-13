from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from database.connection import Base


class PopularMoviesCache(Base):
    __tablename__ = "popular_movies_cache"

    cache_key = Column(String(64), primary_key=True)
    payload = Column(Text, nullable=False)
    total_movies = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)