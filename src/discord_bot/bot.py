import discord
from ..config.settings import DISCORD_BOT_TOKEN

def create_bot():
    """Discord Botクライアントを初期化して返す"""
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Bot(intents=intents)
    return bot

def run_bot(bot: discord.Bot):
    """Botを起動する"""
    if not DISCORD_BOT_TOKEN:
        print("エラー: DISCORD_BOT_TOKENが.envファイルに設定されていません。")
    else:
        bot.run(DISCORD_BOT_TOKEN)