from database.connection import engine, Base, get_db
from modules.users.user_service import UserService
from modules.users.user_model import User
from modules.users.user_movie_preference_model import UserMoviePreference
from modules.movies.movie_model import Movie
from modules.movies.movie_link_model import MovieLink
from modules.movies.movie_service import MovieService
from app import convert_movie_to_json


# Crear tablas
Base.metadata.create_all(bind=engine)

# Ejemplo de uso
if __name__ == "__main__":
    db = next(get_db())
    
    # Obtener película con sus links
    movie_with_links = MovieService.get_movie_with_links(db, 165)
    if movie_with_links:
        print(f"✓ Movie with links: {movie_with_links.title}")
        print(f"  Links: {[(link.imdb_id, link.tmdbId) for link in movie_with_links.movie_links]}")
    else:
        print("No movie found with id 1")
    
    # Obtener película por IMDB ID
    movie_by_imdb = MovieService.get_movie_by_imdb(db, 111161)  # IMDB ID es Integer
    if movie_by_imdb:
        print(f"✓ Found by IMDB: {movie_by_imdb.title}")
    
    # Convertir película a JSON
    if movie_with_links:
        json_movie = convert_movie_to_json(movie_with_links)
        print(f"\n✓ Movie as JSON:")
        print(json_movie)

    db.close()

