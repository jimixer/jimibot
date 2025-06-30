from src.discord_bot.bot import create_bot, run_bot
from src.discord_bot.handlers import register_handlers

def main():
    """アプリケーションのエントリーポイント"""
    bot = create_bot()
    register_handlers(bot)
    run_bot(bot)

if __name__ == "__main__":
    main()