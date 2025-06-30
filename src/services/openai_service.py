import re
import discord
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from ..config.settings import OPENAI_API_KEY
from ..config.prompts import SYSTEM_PROMPT

# メンションを削除するための正規表現をコンパイル
MENTION_PATTERN = re.compile(r'<@!?\d+>')

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_openai_response(history_messages: list, bot_user: discord.ClientUser):
    """
    OpenAI APIを呼び出して応答を取得する。
    history_messages: Discordのメッセージ履歴から整形されたメッセージリスト
    bot_user: Botのユーザーオブジェクト (メッセージの送信者がBot自身であるか判断するため)
    """
    messages_for_api: list[ChatCompletionMessageParam] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history_messages:
        clean_content = MENTION_PATTERN.sub('', msg.content).strip()
        if not clean_content:
            continue

        if msg.author == bot_user:
            messages_for_api.append({"role": "assistant", "content": clean_content})
        else:
            messages_for_api.append({"role": "user", "content": clean_content})

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for_api
    )
    
    reply_content = ""
    if response.choices and response.choices[0].message.content:
        reply_content = response.choices[0].message.content.strip()
    
    return reply_content