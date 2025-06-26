import sqlite3
import argparse
from typing import Optional, Tuple


class DatabaseManager:
    def __init__(self, db_name: str = "objects.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS objects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        photo_url TEXT)''')
        self.conn.commit()

    def reset_table(self):
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS objects")
        self.create_table()
        print("Таблица успешно сброшена!")

    def add_object(self, description: str, photo_url: Optional[str] = None):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO objects (description, photo_url)
                        VALUES (?, ?)''', (description, photo_url))
        self.conn.commit()

    def get_and_delete_random_object(self) -> Optional[Tuple]:
        cursor = self.conn.cursor()

        with self.conn:
            # Выбираем случайный объект
            cursor.execute("SELECT * FROM objects ORDER BY RANDOM() LIMIT 1")
            result = cursor.fetchone()

            if result:
                cursor.execute("DELETE FROM objects WHERE id = ?", (result[0],))
                return result
        return None


def main():
    parser = argparse.ArgumentParser(description="Управление базой данных объектов")
    parser.add_argument('--reset', action='store_true', help="Сбросить таблицу")
    parser.add_argument('--add', nargs='+', metavar=('description', 'photo_url'),
                        help="Добавить объект (описание и ссылка)")
    parser.add_argument('--get', action='store_true', help="Получить случайный объект")
    args = parser.parse_args()

    db = DatabaseManager()

    if args.reset:
        db.reset_table()

    if args.add:
        description = args.add[0]
        photo_url = args.add[1] if len(args.add) > 1 else None
        db.add_object(description, photo_url)
        print(f"Объект добавлен: {description}")

    if args.get:
        obj = db.get_and_delete_random_object()
        if obj:
            print(f"Случайный объект:\nID: {obj[0]}\nОписание: {obj[1]}\nСсылка: {obj[2]}")
        else:
            print("В базе нет объектов")


if __name__ == "__main__":
    main()