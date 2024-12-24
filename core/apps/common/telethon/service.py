from dataclasses import dataclass
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact

from core.apps.customers.entities.customers import CustomerEntity
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

    async def add_contact_and_message(self, client_id: int, phone_number: str, first_name: str, last_name: str, message: str):
        try:
            contact = InputPhoneContact(
                client_id=client_id,
                phone=phone_number,
                first_name=first_name,
                last_name=last_name
            )
            print(contact)
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
        finally:
            await self.client.disconnect()
    async def send_products(self, customer: CustomerEntity, products: list[str], cost: int) -> None:
        await self.start()
        message = self.create_message_for_product(
            customer=customer,
            products=products,
            cost=cost
        )
        await self.add_contact_and_message(
            client_id=customer.id,
            phone_number='+77715716611',
            first_name=customer.first_name,
            last_name=customer.last_name,
            message=message
        )
    def create_message_for_product(self, customer: CustomerEntity, products: list[str], cost: int) -> str:
        message = f"""
{customer.first_name} {customer.last_name}
Phone Number: {customer.phone_number}
Cost: {cost} KZT

Products:
"""
        for product in products:
            message += f"- {product}\n"
    
        return message