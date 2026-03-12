Setup:

Install dependencies: pip install -r requirements.txt
Run the app: python app.py
Access endpoints at http://localhost:5000/endpoint1?text=your_text

Import MovieLens ratings into SQLite:

python scripts/import_ratings.py --truncate

This imports `movielens-20m-dataset/rating.csv` into `db/app.sqlite` table `user_movie_preferences` and sets `updated_at` to `NULL` for imported rows.