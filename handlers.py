from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from config import API_ID, API_HASH
from database import Database

# Создание клиента
client = TelegramClient('session_name', API_ID, API_HASH)
db = Database()

async def fetch_messages(channel_username):
    async with client:
        # Получаем историю сообщений из канала
        channel = await client.get_entity(channel_username)
        history = await client(GetHistoryRequest(
            peer=channel,
            limit=10,  # Количество сообщений для получения
        ))
        messages = []
        for message in history.messages:
            messages.append(f"**{message.sender_id}:** {message.message}\n")
        return messages

async def add_channel(user_id, channel_username):
    db.add_channel(user_id, channel_username)

async def list_channels(user_id):
    return db.get_channels(user_id)

async def remove_channel(user_id, channel_username):
    db.remove_channel(user_id, channel_username)
