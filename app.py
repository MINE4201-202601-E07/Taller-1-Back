from flask import Flask, request, jsonify
from flask_cors import CORS
import random

# Conjunto de películas disponibles
MOVIES = [
    {
        "id": "1",
        "name": "The Shawshank Redemption",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "genre": "Drama",
        "rating": 9.3,
        "imdbLink": "https://www.imdb.com/title/tt0111161/",
        "releaseYear": 1994,
        "director": "Frank Darabont"
    },
    {
        "id": "2",
        "name": "The Godfather",
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his youngest son.",
        "genre": "Crime",
        "rating": 9.2,
        "imdbLink": "https://www.imdb.com/title/tt0068646/",
        "releaseYear": 1972,
        "director": "Francis Ford Coppola"
    },
    {
        "id": "3",
        "name": "The Dark Knight",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological risks.",
        "genre": "Action",
        "rating": 9.0,
        "imdbLink": "https://www.imdb.com/title/tt0468569/",
        "releaseYear": 2008,
        "director": "Christopher Nolan"
    },
    {
        "id": "4",
        "name": "Pulp Fiction",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
        "genre": "Crime",
        "rating": 8.9,
        "imdbLink": "https://www.imdb.com/title/tt0110912/",
        "releaseYear": 1994,
        "director": "Quentin Tarantino"
    },
    {
        "id": "5",
        "name": "Forrest Gump",
        "description": "The presidencies of Kennedy and Johnson unfold from the perspective of an Alabama man with an IQ of 75.",
        "genre": "Drama",
        "rating": 8.8,
        "imdbLink": "https://www.imdb.com/title/tt0109830/",
        "releaseYear": 1994,
        "director": "Robert Zemeckis"
    },
    {
        "id": "6",
        "name": "Inception",
        "description": "A skilled thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
        "genre": "Sci-Fi",
        "rating": 8.8,
        "imdbLink": "https://www.imdb.com/title/tt1375666/",
        "releaseYear": 2010,
        "director": "Christopher Nolan"
    },
    {
        "id": "7",
        "name": "The Matrix",
        "description": "A computer programmer discovers that reality as he knows it is a simulation created by machines.",
        "genre": "Sci-Fi",
        "rating": 8.7,
        "imdbLink": "https://www.imdb.com/title/tt0133093/",
        "releaseYear": 1999,
        "director": "Lana Wachowski, Lilly Wachowski"
    },
    {
        "id": "8",
        "name": "Interstellar",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "genre": "Sci-Fi",
        "rating": 8.6,
        "imdbLink": "https://www.imdb.com/title/tt0816692/",
        "releaseYear": 2014,
        "director": "Christopher Nolan"
    }
]


app = Flask(__name__)
CORS(app)


def startup():
    """Function that runs once when the application starts"""
    print("✓ Application started successfully!")
    print("✓ Server is running on http://localhost:5000")
    print("✓ Available endpoints:")
    print("  - GET /sr_user_user?text=<string>")
    print("  - GET /sr_item_item?text=<string>")
    print("  - GET /resync")
    print("  - GET /health")


@app.route('/sr_user_user', methods=['GET'])
def sr_user_user():
    """First endpoint that returns random movies"""
    limit = request.args.get('limit', default=5, type=int)
    movies_subset = random.sample(MOVIES, min(limit, len(MOVIES)))
    return jsonify({'movies': movies_subset})


@app.route('/sr_item_item', methods=['GET'])
def sr_item_item():
    """Second endpoint that returns random movies"""
    limit = request.args.get('limit', default=5, type=int)
    movies_subset = random.sample(MOVIES, min(limit, len(MOVIES)))
    return jsonify({'movies': movies_subset})


@app.route('/resync', methods=['GET'])
def resync():
    return jsonify({'endpoint': 'resync', 'status': 'resynced'})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    startup()
    app.run(debug=True, port=5000)
