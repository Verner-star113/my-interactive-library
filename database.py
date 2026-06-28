import sqlite3
import random
from datetime import datetime


def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    # Таблица книг со ВСЕМИ нужными столбцами
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
    # Таблица для цитат
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            page TEXT,
            added_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
        )
    """
    )
    # Таблица для сессий таймера
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
    # 4. НОВАЯ: Таблица для томов/частей книги
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS book_volumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            volume_title TEXT NOT NULL,
            book_text TEXT,
            current_position INTEGER DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
        )
    """
    )
    conn.commit()
    conn.close()


def add_book(title, author, status, rating):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO books (title, author, status, rating, added_date) VALUES (?, ?, ?, ?, ?)",
        (title, author, status, rating, current_date),
    )
    conn.commit()
    conn.close()


def get_books():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, author, status, rating, added_date FROM books"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_book_details(book_id, new_status, new_rating):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE books SET status = ?, rating = ? WHERE id = ?",
        (new_status, new_rating, book_id),
    )
    conn.commit()
    conn.close()


def delete_book(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def get_random_wishlist_book():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, author FROM books WHERE status = 'Хочу прочитать'"
    )
    wishlist = cursor.fetchall()
    conn.close()
    if wishlist:
        return random.choice(wishlist)
    return None

# --- ФУНКЦИИ ДЛЯ ЦИТАТ ---
def add_quote(book_id, text, page):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO quotes (book_id, text, page, added_date) VALUES (?, ?, ?, ?)",
        (book_id, text, page, current_date),
    )
    conn.commit()
    conn.close()


def get_all_quotes():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT q.id, b.title, b.author, q.text, q.page, q.added_date 
        FROM quotes q 
        JOIN books b ON q.book_id = b.id
        ORDER BY q.id DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_quote(quote_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()


# --- ФУНКЦИИ ДЛЯ ТАЙМЕРА ---
def add_reading_session(book_id, duration_minutes):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO reading_sessions (book_id, duration_minutes, session_date) VALUES (?, ?, ?)",
        (book_id, duration_minutes, current_date),
    )
    conn.commit()
    conn.close()


def get_total_reading_time():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(duration_minutes) FROM reading_sessions")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0


def get_reader_status_data():
    # 1. Получаем общее время чтения в минутах
    total_minutes = get_total_reading_time()
    if not total_minutes:
        total_minutes = 0

    # 2. Считаем опыт: 1 минута = 10 XP
    total_xp = total_minutes * 10

    # 3. Логика уровней (каждый уровень требует на 200 XP больше)
    # Уровень 1: 0 - 200 XP, Уровень 2: 201 - 500 XP и т.д.
    level = 1
    xp_neededForNext = 200
    temp_xp = total_xp

    while temp_xp >= xp_neededForNext:
        temp_xp -= xp_neededForNext
        level += 1
        xp_neededForNext += 150  # С каждым уровнем планка растет

    # Остаток опыта для текущего уровня и процент прогресса
    current_level_xp = temp_xp
    progress_percent = int((current_level_xp / xp_neededForNext) * 100) if xp_neededForNext > 0 else 100

    # 4. Система рангов и званий на основе начитанных минут
    if total_minutes == 0:
        rank_name = "Книжный червячок 🐛"
        rank_desc = "Вы только начали свой путь. Время открыть первый свиток!"
        stars = 0
    elif total_minutes < 30:
        rank_name = "Искатель историй 🔍"
        rank_desc = "Вы присматриваетесь к книжным полкам. Не останавливайтесь!"
        stars = 1
    elif total_minutes < 120:
        rank_name = "Хранитель библиотек 🏛️"
        rank_desc = "Книги начали доверять вам свои первые секреты."
        stars = 2
    elif total_minutes < 500:
        rank_name = "Повелитель страниц 📜"
        rank_desc = "Вы читаете быстрее, чем ветер листает осенние листья."
        stars = 3
    elif total_minutes < 1000:
        rank_name = "Рыцарь Чернильного ордена ⚔️"
        rank_desc = "Ваша начитанность способна сокрушить любое невежество."
        stars = 4
    else:
        rank_name = "Магистр тайных фолиантов 🔮"
        rank_desc = "Вы достигли вершины книжного просветления. Архивы мира покорны вам!"
        stars = 5

    return {
        "minutes": total_minutes,
        "xp": total_xp,
        "level": level,
        "next_level_xp": xp_neededForNext,
        "current_level_xp": current_level_xp,
        "progress": progress_percent,
        "rank": rank_name,
        "desc": rank_desc,
        "stars": stars
    }


def update_book_position(book_id, position):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    # Если пришел кортеж (например, (1,)), берем его первый элемент. Иначе переводим в int.
    clean_id = int(book_id[0]) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "UPDATE books SET current_position = ? WHERE id = ?",
        (position, clean_id),
    )
    conn.commit()
    conn.close()


def get_book_position(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id[0]) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "SELECT current_position FROM books WHERE id = ?", (clean_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] is not None else 0


def save_book_text(book_id, text):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id[0]) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "UPDATE books SET book_text = ? WHERE id = ?",
        (text, clean_id)
    )
    conn.commit()
    conn.close()


def get_book_text(book_id):
    conn = sqlite3.connect("library.db", timeout=10)
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute("SELECT book_text FROM books WHERE id = ?", (clean_id,))
    result = cursor.fetchone()
    conn.close()
    # Достаем чистый текст из кортежа result[0]
    return result[0] if result and result[0] is not None else None

# --- НОВЫЕ ФУНКЦИИ ДЛЯ МНОГОТОМНОСТИ ---
def add_book_volume(book_id, volume_title, text):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "INSERT INTO book_volumes (book_id, volume_title, book_text) VALUES (?, ?, ?)",
        (clean_id, volume_title, text),
    )
    conn.commit()
    conn.close()


def get_book_volumes(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "SELECT id, volume_title FROM book_volumes WHERE book_id = ?",
        (clean_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_volume_data(volume_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT book_text, current_position FROM book_volumes WHERE id = ?",
        (int(volume_id),),
    )
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, 0)


def update_volume_position(volume_id, position):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE book_volumes SET current_position = ? WHERE id = ?",
        (position, int(volume_id)),
    )
    conn.commit()
    conn.close()


def delete_book_volume(volume_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM book_volumes WHERE id = ?", (int(volume_id),))
    conn.commit()
    conn.close()

# --- НОВЫЕ ФУНКЦИИ ДЛЯ СМЕНЫ РЕЖИМА МНОГОТОМНОСТИ НА ОБЫЧНЫЙ И НАОБОРОТ ---
def update_book_series_mode(book_id, is_series_value):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "UPDATE books SET is_series = ? WHERE id = ?",
        (int(is_series_value), clean_id),
    )
    conn.commit()
    conn.close()


def get_book_series_mode(book_id):
    conn = sqlite3.connect("library.db", timeout=10)
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute("SELECT is_series FROM books WHERE id = ?", (clean_id,))
    result = cursor.fetchone()
    conn.close()
    # Достаем первый элемент кортежа result[0] (0 или 1)
    return result[0] if result and result[0] is not None else 0


def update_book_notes(book_id, notes):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute(
        "UPDATE books SET book_notes = ? WHERE id = ?",
        (notes, clean_id)
    )
    conn.commit()
    conn.close()


def get_book_notes(book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    clean_id = int(book_id) if isinstance(book_id, tuple) else int(book_id)
    cursor.execute("SELECT book_notes FROM books WHERE id = ?", (clean_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else ""
