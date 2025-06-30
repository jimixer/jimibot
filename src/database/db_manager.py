import os
import aiosqlite
from datetime import datetime
from src.config.settings import DB_PATH

async def init_database():
    """データベースとテーブルを初期化する"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    author TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            await db.commit()
        print("データベースが正常に初期化されました。")
    except aiosqlite.Error as e:
        print(f"データベース初期化エラー: {e}")

async def save_message_to_db(author: str, content: str):
    """メッセージをデータベースに保存する"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO messages (timestamp, author, content) VALUES (?, ?, ?)",
                (timestamp, author, content)
            )
            await db.commit()
    except aiosqlite.Error as e:
        print(f"データベースエラー: {e}")