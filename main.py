from database.connection import engine, Base, get_db
from modules.users.user_service import UserService
from modules.users.user_model import User
from modules.users.user_movie_preference_model import UserMoviePreference

# Crear tablas
Base.metadata.create_all(bind=engine)

# Ejemplo de uso
if __name__ == "__main__":
    db = next(get_db())
    user = UserService.create_user(db, "test@example.com", "John Doe", "password123")
    print(f"User created: {user.id} - {user.email}")