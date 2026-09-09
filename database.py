import mysql.connector


class DatabaseUnavailableError(RuntimeError):
    pass


class DictionaryRepository:
    def __init__(self, config):
        self.connection_config = {
            "host": config["DB_HOST"],
            "port": config["DB_PORT"],
            "user": config["DB_USER"],
            "password": config["DB_PASSWORD"],
            "database": config["DB_NAME"],
        }
        self._cache = None

    def get_all(self):
        if self._cache is None:
            self._cache = self._load()
        return self._cache

    def clear_cache(self):
        self._cache = None

    def _load(self):
        try:
            connection = mysql.connector.connect(**self.connection_config)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT kata_indo, kata_minang, kategori FROM indonesia"
            )
            indonesia_rows = cursor.fetchall()
            cursor.execute(
                "SELECT kata_minang, kata_indo, kategori FROM minangkabau"
            )
            minangkabau_rows = cursor.fetchall()
        except mysql.connector.Error as error:
            raise DatabaseUnavailableError(str(error)) from error
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals() and connection.is_connected():
                connection.close()

        indonesia_to_minang = {
            indonesia.strip().lower(): minang.strip().lower()
            for indonesia, minang, _ in indonesia_rows
            if indonesia and minang
        }
        minang_to_indonesia = {
            minang.strip().lower(): indonesia.strip().lower()
            for minang, indonesia, _ in minangkabau_rows
            if minang and indonesia
        }
        minang_categories = {
            minang.strip().lower(): category
            for minang, _, category in minangkabau_rows
            if minang and category
        }

        return indonesia_to_minang, minang_to_indonesia, minang_categories
