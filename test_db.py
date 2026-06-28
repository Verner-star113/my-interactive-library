import unittest
import sqlite3
import os
# Импортируем функции из модуля database.py
from database import add_book, get_books, get_reader_status_data


class TestLibraryDatabase(unittest.TestCase):

    def setUp(self):
        """Выполняется перед каждым тестом. Создаем чистую тестовую базу."""
        self.db_name = "library.db"
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS books")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                status TEXT NOT NULL,
                rating INTEGER DEFAULT 0,
                added_date TEXT,
                current_position INTEGER DEFAULT 0,
                book_text TEXT,
                is_series INTEGER DEFAULT 0,
                book_notes TEXT
            )
        """
        )
        cursor.execute("DROP TABLE IF EXISTS reading_sessions")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                duration_minutes INTEGER NOT NULL,
                session_date TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
            )
        """
        )
        conn.commit()
        conn.close()

    def test_add_and_get_book(self):
        """Тестируем корректность добавления и чтения книги."""
        # Изначально база должна быть пустой
        books_before = get_books()
        self.assertEqual(len(books_before), 0)

        # Добавляем книгу
        add_book("Капитанская дочка", "Александр Пушкин", "Хочу прочитать", 0)

        # Теперь в базе должна быть ровно 1 запись
        books_after = get_books()
        self.assertEqual(len(books_after), 1)
        # Проверяем название добавленной книги (оно идет вторым элементом в кортеже)
        self.assertEqual(books_after[0][1], "Капитанская дочка")

    def test_initial_reader_status(self):
        """Тестируем стартовый игровой статус нового читателя."""
        status = get_reader_status_data()
        self.assertEqual(status["level"], 1)
        self.assertEqual(status["minutes"], 0)
        self.assertEqual(status["xp"], 0)
        self.assertIn("Книжный червячок", status["rank"])


if __name__ == "__main__":
    unittest.main()
