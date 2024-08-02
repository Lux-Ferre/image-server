import sqlite3
import bcrypt

from datetime import datetime, UTC


class SQLiteDB:
    def __init__(self, db_loc: str):
        self.connection = None
        self.loc = db_loc

    def __enter__(self):
        try:
            def adapt_datetime_epoch(val):
                """Adapt datetime.datetime to Unix timestamp."""
                return int(val.timestamp())

            def convert_timestamp(val):
                """Convert Unix epoch timestamp to datetime.datetime object."""
                return datetime.fromtimestamp(int(val), UTC)

            sqlite3.register_adapter(datetime, adapt_datetime_epoch)
            sqlite3.register_converter("timestamp", convert_timestamp)

            self.connection = sqlite3.connect(self.loc, detect_types=sqlite3.PARSE_DECLTYPES)

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
                datetime timestamp NOT NULL UNIQUE
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS session_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                expiry timestamp NOT NULL
            )
        """)

        self.connection.commit()

    def add_image(self, filename: str, uuid: str, date: datetime):
        cursor = self.connection.cursor()
        query = f"INSERT INTO images (filename, uuid, datetime) VALUES (?, ?, ?)"
        params = (filename, uuid, date)
        cursor.execute(query, params)
        self.connection.commit()

    def get_image_data(self, uuid: str) -> dict[str, datetime] | None:
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

    def add_token(self, username: str, token: str, expiry: datetime):
        salt = bcrypt.gensalt()
        hashed_token = bcrypt.hashpw(token.encode('utf-8'), salt)

        cursor = self.connection.cursor()
        query = f"INSERT INTO session_tokens (token, username, expiry) VALUES (?, ?, ?) RETURNING id"
        params = (hashed_token, username, expiry)
        ident = cursor.execute(query, params).fetchone()[0]
        self.connection.commit()

        return ident

    def find_token(self, ident: int) -> tuple[bytes, datetime]:
        cursor = self.connection.cursor()
        query = f"SELECT token, expiry FROM session_tokens WHERE id=?"
        params = (ident,)
        result = cursor.execute(query, params).fetchone()

        return result

    def is_valid_token(self, ident: int, token: str):
        token_data = self.find_token(ident)
        if token_data is None:
            return False
        if token_data[1] < datetime.now(UTC):
            self.delete_token(ident)
            return False

        hashed_token = token_data[0]
        return bcrypt.checkpw(token.encode('utf-8'), hashed_token)

    def delete_token(self, ident: int):
        cursor = self.connection.cursor()
        query = f"DELETE FROM session_tokens WHERE id=?"
        params = (ident,)
        cursor.execute(query, params)
        self.connection.commit()

    def flush_tokens(self):
        cursor = self.connection.cursor()
        query = f"DELETE FROM session_tokens WHERE 1"
        cursor.execute(query)
        count = cursor.execute("SELECT changes()").fetchone()[0]
        print(f"{count} session tokens have been flushed from the database.")
        self.connection.commit()
