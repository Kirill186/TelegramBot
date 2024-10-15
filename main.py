import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH
from handlers import fetch_messages, add_channel, list_channels, remove_channel

client = TelegramClient('session_name', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Привет! Я бот для получения новостей из Telegram-каналов.\n"
                        "Используйте /add <канал> для добавления канала.\n"
                        "Используйте /list для отображения добавленных каналов.\n"
                        "Используйте /remove <канал> для удаления канала.")

@client.on(events.NewMessage(pattern='/add (.*)'))
async def add(event):
    channel_username = event.pattern_match.group(1)
    user_id = event.sender_id
    await add_channel(user_id, channel_username)
    await event.respond(f"Канал {channel_username} был добавлен.")

@client.on(events.NewMessage(pattern='/list'))
async def list(event):
    user_id = event.sender_id
    channels = await list_channels(user_id)
    if channels:
        await event.respond("Ваши добавленные каналы:\n" + "\n".join(channels))
    else:
        await event.respond("У вас нет добавленных каналов.")

@client.on(events.NewMessage(pattern='/remove (.*)'))
async def remove(event):
    channel_username = event.pattern_match.group(1)
    user_id = event.sender_id
    await remove_channel(user_id, channel_username)
    await event.respond(f"Канал {channel_username} был удален.")

async def main():
    await client.start()
    print("Бот запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
