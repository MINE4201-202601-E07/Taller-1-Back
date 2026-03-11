from sqlalchemy.orm import Session
from modules.movies.movie_model import Movie
from modules.movies.movie_link_model import MovieLink


class MovieService:
    @staticmethod
    def get_movie_with_links(db: Session, movie_id: int):
        """Obtiene una película con todos sus links en un solo objeto"""
        return db.query(Movie).filter(Movie.movie_id == movie_id).first()

    @staticmethod
    def get_all_movies_with_links(db: Session):
        """Obtiene todas las películas con sus links"""
        return db.query(Movie).all()

    @staticmethod
    def create_movie(db: Session, movie_id: int, title: str, genres: str = None):
        """Crea una nueva película"""
        movie = Movie(
            movie_id=movie_id,
            title=title,
            genres=genres
        )
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def update_movie(db: Session, movie_id: int, title: str = None, genres: str = None):
        """Actualiza una película existente"""
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if movie:
            if title:
                movie.title = title
            if genres:
                movie.genres = genres
            db.commit()
            db.refresh(movie)
        return movie

    @staticmethod
    def add_link_to_movie(db: Session, movie_id: int, imdb_id: int, tmdb_id: int = None):
        """Agrega un link a una película"""
        link = MovieLink(movie_id=movie_id, imdb_id=imdb_id, tmdbId=tmdb_id)
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def get_movie_by_imdb(db: Session, imdb_id: int):
        """Obtiene una película por su IMDB ID"""
        link = db.query(MovieLink).filter(MovieLink.imdb_id == imdb_id).first()
        if link:
            return link.movie
        return None

    @staticmethod
    def delete_movie(db: Session, movie_id: int):
        """Elimina una película (y sus links por cascade)"""
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if movie:
            db.delete(movie)
            db.commit()
            return True
        return False

