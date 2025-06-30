import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID") or "")
except (ValueError, TypeError):
    print("エラー: TARGET_CHANNEL_IDが.envファイルに正しく設定されていません。")
    exit()

DB_PATH = "data/bot_database.db"

RANDOM_MESSAGES = [
    "今日も一日頑張りましょう！",
    "何か面白いことないかな？",
    "コーヒーでも飲んで一息つきますか。",
    "今日の進捗どうですか？",
    "お腹すいたな…",
]

PROMPT_PATH = "config/persona.md"