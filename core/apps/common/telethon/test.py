import asyncio
from dataclasses import dataclass
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from ....core.settings.main import env

@dataclass
class TelegramConfig:
    api_id: str = env('API_ID')
    api_hash: str = env('API_HASH')
    bot_token: str = None 
    session_name: str = "default_session"


class TelegramService:
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.client: TelegramClient = None
    async def start(self):
        if self.config.bot_token:
            self.client = await TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash,
                
            ).start(bot_token=self.config.bot_token)
        else:
            self.client = await TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash
            ).start()
            
            

    async def send_message(self, recipient: str, message: str):
        try:
            await self.client.send_message(recipient, message)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    async def add_contact_and_message(self, client_id, phone_number: str, first_name: str, last_name: str, message: str):
        try:
            contact = InputPhoneContact(
                client_id=client_id,
                phone=phone_number,
                first_name=first_name,
                last_name=last_name
            )
            result = await self.client(ImportContactsRequest([contact]))
            if result.users:
                user = result.users[0]
                await self.send_message(user.id, message)
                print(f"Сообщение отправлено контакту: {phone_number}")
                await self.client(DeleteContactsRequest([user]))
            else:
                print(f"Контакт с номером {phone_number} не найден.")
        except Exception as e:
            print(f"Ошибка при работе с контактом: {e}")



async def main():
    config = TelegramConfig() 
    telegram_service = TelegramService(config)
    await telegram_service.start()  

    try:
        await telegram_service.send_message("+77713817316", "Привет! Это тестовое сообщение.")
        await telegram_service.add_contact_and_message(
            phone_number="+77713817316",
            first_name="Имя",
            last_name="Фамилия",
            message="Привет INDIRA!"
        )
    finally:
        print('popa')

if __name__ == "__main__":
    asyncio.run(main())