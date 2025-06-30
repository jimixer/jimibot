import os
import random
import re
import asyncio
import aiosqlite
from datetime import datetime

import discord
from dotenv import load_dotenv
from openai import AsyncOpenAI

# --- 初期設定 ---

# .envファイルから環境変数を読み込む
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID") or "")
except (ValueError, TypeError):
    print("エラー: TARGET_CHANNEL_IDが.envファイルに正しく設定されていません。")
    exit()

# Botのインテントを設定
intents = discord.Intents.default()
intents.message_content = True

# BotクライアントとOpenAIクライアントを初期化
bot = discord.Bot(intents=intents) 
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

DB_PATH = "data/bot_database.db"

# 定期投稿用のメッセージリスト
RANDOM_MESSAGES = [
    "今日も一日頑張りましょう！",
    "何か面白いことないかな？",
    "コーヒーでも飲んで一息つきますか。",
    "今日の進捗どうですか？",
    "お腹すいたな…",
]

# --- プロンプト関連 ---
PROMPT_PATH = "config/persona.md"
SYSTEM_PROMPT = ""

def load_system_prompt():
    """システムプロンプトをファイルから読み込む"""
    global SYSTEM_PROMPT
    try:
        # srcディレクトリから見た相対パスでconfig/persona.mdを指定
        config_path = os.path.join(os.path.dirname(__file__), '..', PROMPT_PATH)
        with open(config_path, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read()
        print(f"システムプロンプトを '{config_path}' から読み込みました。")
    except FileNotFoundError:
        print(f"エラー: プロンプトファイル '{PROMPT_PATH}' が見つかりません。デフォルトのプロンプトを使用します。")
        SYSTEM_PROMPT = "あなたは親切で少しユーモアのあるアシスタントです。"
    except Exception as e:
        print(f"プロンプトファイルの読み込み中にエラーが発生しました: {e}。デフォルトのプロンプトを使用します。")
        SYSTEM_PROMPT = "あなたは親切で少しユーモアのあるアシスタントです。"

# --- データベース関連 ---

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

# --- Discord Bot イベント ---

@bot.event
async def on_ready():
    """Botが起動したときに実行される"""
    print(f"Bot is ready. Logged in as {bot.user}")
    load_system_prompt()
    await init_database()
    bot.loop.create_task(send_random_message_loop())

async def send_random_message_loop():
    """ランダムなメッセージを定期的に送信するループ"""
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print(f"エラー: チャンネルID {TARGET_CHANNEL_ID} が見つかりません。")
        return

    while not bot.is_closed():
        # 起動直後に投稿しないよう、先に待機する
        sleep_duration = random.randint(3600, 7200)  # 1〜2時間
        await asyncio.sleep(sleep_duration)

        message_content = random.choice(RANDOM_MESSAGES)
        try:
            await channel.send(message_content)
            await save_message_to_db(str(bot.user), message_content)
        except discord.Forbidden:
            print(f"エラー: チャンネル {channel.name} へのメッセージ送信権限がありません。")
        except Exception as e:
            print(f"ランダムメッセージ送信中にエラーが発生しました: {e}")

@bot.event
async def on_message(message: discord.Message):
    """メッセージを受信したときに実行される"""
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return

    # DMでの会話、またはチャンネルでのメンションに応答
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = bot.user.mentioned_in(message)

    if is_dm or is_mentioned:
        # ユーザーのメッセージをDBに保存
        await save_message_to_db(str(message.author), message.content)

        # 応答生成中であることをユーザーに伝える (async with を使用)
        async with message.channel.typing():
            try:
                # 直近5件の会話履歴を取得してAPIに渡す準備
                history = [msg async for msg in message.channel.history(limit=5)]
                history.reverse() # 時系列順にする

                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in history:
                    role = "assistant" if msg.author == bot.user else "user"
                    # メンション部分を会話履歴から取り除く
                    clean_content = re.sub(r'<@!?\d+>', '', msg.content).strip()
                    if clean_content: # 空のメッセージはAPIに送らない
                        messages_for_api.append({"role": role, "content": clean_content})

                # OpenAI APIにリクエストを送信
                response = await openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages_for_api)
                
                # 応答が正常に得られたかを確認し、内容を安全に取得する
                reply_content = ""
                if response.choices and response.choices[0].message.content:
                    reply_content = response.choices[0].message.content.strip()
                
                # 応答を送信し、DBに保存
                await message.reply(reply_content)
                await save_message_to_db(str(bot.user), reply_content)

            except Exception as e:
                print(f"OpenAI API呼び出し中にエラーが発生しました: {e}")
                await message.reply("ごめんなさい、ちょっと考えごとをしていました。もう一度話しかけてみてください。")

# --- Botの起動 ---
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("エラー: DISCORD_BOT_TOKENが.envファイルに設定されていません。")
    else:
        bot.run(DISCORD_BOT_TOKEN)