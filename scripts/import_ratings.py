#!/usr/bin/env python3
"""Bulk import MovieLens ratings into user_movie_preferences."""

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Iterable, List, Tuple


def chunked(rows: Iterable[Tuple[int, str, float, str]], size: int):
    batch: List[Tuple[int, str, float, str]] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def parse_csv(csv_path: Path) -> Iterable[Tuple[int, str, float, str]]:
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_headers = {"userId", "movieId", "rating", "timestamp"}
        if not expected_headers.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                "CSV headers must include userId,movieId,rating,timestamp"
            )

        for row in reader:
            # Keep movie_id as string to match the SQLAlchemy model definition.
            yield (
                int(row["userId"]),
                row["movieId"],
                float(row["rating"]),
                row["timestamp"],
            )


def import_ratings(db_path: Path, csv_path: Path, truncate: bool, batch_size: int) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")

        if truncate:
            cursor.execute("DELETE FROM user_movie_preferences;")
            conn.commit()

        sql = """
            INSERT INTO user_movie_preferences
                (user_id, movie_id, rating, liked, visited, created_at, updated_at)
            VALUES (?, ?, ?, NULL, NULL, ?, NULL)
        """

        users_sql = """
            INSERT OR IGNORE INTO users (id, email, name, password, created_at)
            VALUES (?, ?, ?, '', CURRENT_TIMESTAMP)
        """

        total = 0
        for batch in chunked(parse_csv(csv_path), batch_size):
            users_batch = [
                (uid, f"movielens_user_{uid}@import.local", f"MovieLens User {uid}")
                for uid in {row[0] for row in batch}
            ]
            cursor.executemany(users_sql, users_batch)
            cursor.executemany(sql, batch)
            total += len(batch)
            conn.commit()

        print(f"Imported {total} ratings into user_movie_preferences")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import MovieLens ratings.csv into db/app.sqlite:user_movie_preferences"
    )
    parser.add_argument(
        "--db-path",
        default="db/app.sqlite",
        help="Path to SQLite database (default: db/app.sqlite)",
    )
    parser.add_argument(
        "--csv-path",
        default="movielens-20m-dataset/rating.csv",
        help="Path to ratings CSV (default: movielens-20m-dataset/rating.csv)",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Delete existing rows from user_movie_preferences before import",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Number of rows per insert batch (default: 5000)",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    csv_path = Path(args.csv_path)

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    import_ratings(db_path=db_path, csv_path=csv_path, truncate=args.truncate, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
