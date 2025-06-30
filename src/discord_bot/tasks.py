import asyncio
import random
import discord
from ..config.settings import TARGET_CHANNEL_ID, RANDOM_MESSAGES
from ..database.db_manager import save_message_to_db

async def send_random_message_loop(bot: discord.Bot):
    """ランダムなメッセージを定期的に送信するループ"""
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print(f"エラー: チャンネルID {TARGET_CHANNEL_ID} が見つかりません。")
        return

    while not bot.is_closed():
        sleep_duration = random.randint(3600, 7200)  # 1〜2時間
        await asyncio.sleep(sleep_duration)

        message_content = random.choice(RANDOM_MESSAGES)
        try:
            # channelがTextChannelまたはDMChannelであることを確認
            if isinstance(channel, (discord.TextChannel, discord.DMChannel)):
                await channel.send(message_content)
                await save_message_to_db(str(bot.user), message_content)
            else:
                print(f"エラー: チャンネル (ID: {channel.id}, タイプ: {type(channel).__name__}) はメッセージ送信に対応していません。")
        except discord.Forbidden:
            print(f"エラー: チャンネル (ID: {channel.id}, タイプ: {type(channel).__name__}) へのメッセージ送信権限がありません。")
        except Exception as e:
            print(f"ランダムメッセージ送信中にエラーが発生しました: {e}")