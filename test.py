from telethon import TelegramClient

# Указываем API_ID и API_HASH
API_ID = '25097275'
API_HASH = 'd855d5e8b2accbd1f09c44646cc767d9'

# Создаем клиента
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    # Подключаемся и выводим информацию о пользователе
    await client.start()
    me = await client.get_me()
    print(f'Ваше имя: {me.first_name}')
    print(f'Ваш ID: {me.id}')

# Запуск клиента
with client:
    client.loop.run_until_complete(main())









