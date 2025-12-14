# database.py
import sqlite3
from typing import List, Optional, Tuple, Any

DATABASE_FILE = "bokelai.db"

def get_db_connection() -> sqlite3.Connection:
    """
    建立並回傳 SQLite 資料庫連線。

    設定 row_factory 為 sqlite3.Row，使結果可以像字典一樣存取。

    :return: SQLite 資料庫連線物件
    """
    conn = sqlite3.connect(DATABASE_FILE)
    # 必須設定 row_factory = sqlite3.Row
    conn.row_factory = sqlite3.Row
    return conn

def get_all_books(skip: int = 0, limit: int = 100) -> List[sqlite3.Row]:
    """
    分頁取得書籍列表。

    :param skip: 跳過的記錄數 (OFFSET)。
    :param limit: 取得的記錄數 (LIMIT)。
    :return: 書籍列表 (List[sqlite3.Row])。
    """
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM books ORDER BY id LIMIT ? OFFSET ?", (limit, skip)
    )
    books = cursor.fetchall()
    conn.close()
    return books

def get_book_by_id(book_id: int) -> Optional[sqlite3.Row]:
    """
    根據 ID 取得單一書籍。

    :param book_id: 書籍的 ID。
    :return: 單一書籍記錄 (sqlite3.Row)，如果不存在則為 None。
    """
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book

def create_book(book_data: dict) -> int:
    """
    新增一本書籍記錄。

    :param book_data: 包含書籍資料的字典。
    :return: 新增書籍的 ID。
    """
    conn = get_db_connection()
    # 移除 None 值，避免 SQL 錯誤
    filtered_data = {k: v for k, v in book_data.items() if v is not None}
    
    columns = ', '.join(filtered_data.keys())
    placeholders = ', '.join(['?'] * len(filtered_data))
    values = tuple(filtered_data.values())

    conn.execute(
        f"INSERT INTO books ({columns}) VALUES ({placeholders})", values
    )
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return new_id

def update_book(book_id: int, book_data: dict) -> bool:
    """
    完整更新一本書籍記錄 (所有欄位)。

    :param book_id: 要更新的書籍 ID。
    :param book_data: 包含書籍資料的字典。
    :return: 如果更新成功 (影響 1 條記錄) 則為 True，否則為 False。
    """
    conn = get_db_connection()
    
    # 排除 id 和 created_at 等不應更新的欄位
    update_data = {k: v for k, v in book_data.items() if k not in ['id', 'created_at']}
    
    set_clauses = ', '.join([f"{key} = ?" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(book_id)

    cursor = conn.execute(
        f"UPDATE books SET {set_clauses} WHERE id = ?", tuple(values)
    )
    conn.commit()
    updated = cursor.rowcount == 1
    conn.close()
    return updated

def delete_book(book_id: int) -> bool:
    """
    根據 ID 刪除一本書籍記錄。

    :param book_id: 要刪除的書籍 ID。
    :return: 如果刪除成功 (影響 1 條記錄) 則為 True，否則為 False。
    """
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    deleted = cursor.rowcount == 1
    conn.close()
    return deleted