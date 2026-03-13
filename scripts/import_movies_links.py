#!/usr/bin/env python3
"""Bulk import MovieLens movie.csv and link.csv into movie and movie_link tables."""

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple


MovieRow = Tuple[int, str, str]
MovieLinkRow = Tuple[int, int, Optional[int]]


def chunked(rows: Iterable[Tuple], size: int) -> Iterator[List[Tuple]]:
    batch: List[Tuple] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def parse_movies_csv(csv_path: Path) -> Iterable[MovieRow]:
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_headers = {"movieId", "title", "genres"}
        if not expected_headers.issubset(set(reader.fieldnames or [])):
            raise ValueError("movie.csv headers must include movieId,title,genres")

        for row in reader:
            yield (
                int(row["movieId"]),
                row["title"],
                row["genres"],
            )


def parse_links_csv(csv_path: Path) -> Iterable[MovieLinkRow]:
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_headers = {"movieId", "imdbId", "tmdbId"}
        if not expected_headers.issubset(set(reader.fieldnames or [])):
            raise ValueError("link.csv headers must include movieId,imdbId,tmdbId")

        for row in reader:
            imdb_raw = row["imdbId"].strip()
            if not imdb_raw:
                continue

            tmdb_raw = row["tmdbId"].strip()
            tmdb_id = int(tmdb_raw) if tmdb_raw else None
            yield (
                int(row["movieId"]),
                int(imdb_raw),
                tmdb_id,
            )


def import_movies(
    conn: sqlite3.Connection,
    movies_csv: Path,
    batch_size: int,
) -> int:
    movie_sql = """
        INSERT OR REPLACE INTO movie (movie_id, title, genres)
        VALUES (?, ?, ?)
    """

    total = 0
    cursor = conn.cursor()
    for batch in chunked(parse_movies_csv(movies_csv), batch_size):
        cursor.executemany(movie_sql, batch)
        total += len(batch)
        conn.commit()
    return total


def import_links(
    conn: sqlite3.Connection,
    links_csv: Path,
    batch_size: int,
) -> int:
    link_sql = """
        INSERT OR REPLACE INTO movie_link (movie_id, imdb_id, tmdbId)
        VALUES (?, ?, ?)
    """

    total = 0
    cursor = conn.cursor()
    for batch in chunked(parse_links_csv(links_csv), batch_size):
        cursor.executemany(link_sql, batch)
        total += len(batch)
        conn.commit()
    return total


def run_import(
    db_path: Path,
    movies_csv: Path,
    links_csv: Path,
    truncate: bool,
    batch_size: int,
) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")

        if truncate:
            cursor.execute("DELETE FROM movie_link;")
            cursor.execute("DELETE FROM movie;")
            conn.commit()

        imported_movies = import_movies(conn, movies_csv, batch_size)
        imported_links = import_links(conn, links_csv, batch_size)

        print(f"Imported/updated {imported_movies} rows in movie")
        print(f"Imported/updated {imported_links} rows in movie_link")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import MovieLens movie.csv and link.csv into db/app.sqlite"
    )
    parser.add_argument(
        "--db-path",
        default="db/app.sqlite",
        help="Path to SQLite database (default: db/app.sqlite)",
    )
    parser.add_argument(
        "--movies-csv",
        default="movielens-20m-dataset/movie.csv",
        help="Path to movie.csv (default: movielens-20m-dataset/movie.csv)",
    )
    parser.add_argument(
        "--links-csv",
        default="movielens-20m-dataset/link.csv",
        help="Path to link.csv (default: movielens-20m-dataset/link.csv)",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Delete existing rows from movie and movie_link before import",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Rows per insert batch (default: 5000)",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    movies_csv = Path(args.movies_csv)
    links_csv = Path(args.links_csv)

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    if not movies_csv.exists():
        raise FileNotFoundError(f"movie.csv not found: {movies_csv}")
    if not links_csv.exists():
        raise FileNotFoundError(f"link.csv not found: {links_csv}")

    run_import(
        db_path=db_path,
        movies_csv=movies_csv,
        links_csv=links_csv,
        truncate=args.truncate,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
