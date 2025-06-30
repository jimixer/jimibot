import discord
from ..database.db_manager import save_message_to_db
from ..services.openai_service import get_openai_response

def register_handlers(bot: discord.Bot):
    """Discord Botのイベントハンドラを登録する"""

    @bot.event
    async def on_ready():
        """Botが起動したときに実行される"""
        from ..config.prompts import load_system_prompt
        from ..database.db_manager import init_database
        from .tasks import send_random_message_loop

        print(f"Bot is ready. Logged in as {bot.user}")
        load_system_prompt()
        await init_database()
        bot.loop.create_task(send_random_message_loop(bot))

    @bot.event
    async def on_message(message: discord.Message):
        """メッセージを受信したときに実行される"""
        if message.author == bot.user:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = bot.user and bot.user.mentioned_in(message)

        if is_dm or is_mentioned:
            if bot.user is None:
                print("エラー: BotユーザーがNoneです。")
                return

            await save_message_to_db(str(message.author), message.content)

            async with message.channel.typing():
                try:
                    history = [msg async for msg in message.channel.history(limit=5)]
                    history.reverse()

                    reply_content = await get_openai_response(history, bot.user)
                    
                    await message.reply(reply_content)
                    await save_message_to_db(str(bot.user), reply_content)

                except Exception as e:
                    print(f"メッセージ処理中にエラーが発生しました: {e}")
                    await message.reply("ごめんなさい、ちょっと考えごとをしていました。もう一度話しかけてみてください。")