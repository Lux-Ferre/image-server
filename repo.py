import sqlite3

from datetime import datetime


class SQLiteDB:
    def __init__(self, db_loc: str):
        self.connection = None
        self.loc = db_loc

    def __enter__(self):
        try:
            self.connection = sqlite3.connect(self.loc)

            return self
        except sqlite3.Error as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def init_db(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL UNIQUE,
                datetime TEXT NOT NULL UNIQUE
            )
        """)

    def add_image(self, filename: str, uuid: str, date: datetime):
        cursor = self.connection.cursor()
        query = f"INSERT INTO images (filename, uuid, datetime) VALUES (?, ?, ?)"
        params = (filename, uuid, date)
        cursor.execute(query, params)
        self.connection.commit()

    def get_image_data(self, uuid: str) -> dict[str, str] | None:
        cursor = self.connection.cursor()
        query = f"SELECT filename, datetime FROM images WHERE uuid=?"
        params = (uuid,)
        result = cursor.execute(query, params).fetchone()

        if result is None:
            return None

        data = {
            'filename': result[0],
            'date': result[1]
        }
        return data

    def get_all_images(self):
        cursor = self.connection.cursor()
        query = f"SELECT uuid, filename, datetime FROM images"
        result = cursor.execute(query).fetchall()

        return result
