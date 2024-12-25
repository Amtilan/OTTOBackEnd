from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from core.apps.common.telethon.service import TelegramConfig, TelegramService
from core.apps.customers.entities.customers import CustomerEntity


class BaseSendersService(ABC):
    @abstractmethod
    async def send_auth_code(self, auth_code: str, Customer: CustomerEntity) -> None:
        ...


class DummySendersService(BaseSendersService):
    async def send_auth_code(self, auth_code: str, Customer: CustomerEntity) -> None:
        print(f"Sending {Customer=} auth code {auth_code=}")

class EmailSendersService(BaseSendersService):
    async def send_auth_code(self, Customer: CustomerEntity, auth_code: str) -> None:
        print(f"Sending {Customer=} auth code {auth_code=}")

class PushSendersService(BaseSendersService):
    async def send_auth_code(self, Customer: CustomerEntity, auth_code: str) -> None:
        print(f"Sending push notification auth code {auth_code=}")

class TGSenderService(BaseSendersService):
    async def send_auth_code(self, Customer: CustomerEntity, auth_code: str) -> None:
        tg_service: TelegramService = TelegramService(config=TelegramConfig())
        await tg_service.start()
        try:
            await tg_service.add_contact_and_message(
                client_id=Customer.id,
                phone_number=Customer.phone_number,
                first_name=Customer.first_name,
                last_name=Customer.last_name,
                message=auth_code,
            )
        finally:
            print(f'Sending Auth Code to {Customer=}')
    async def send_new_password(self, Customer: CustomerEntity) -> None:
        tg_service: TelegramService = TelegramService(config=TelegramConfig())
        await tg_service.start()
        try:
            await tg_service.add_contact_and_message(
                client_id=Customer.id,
                phone_number=Customer.phone_number,
                first_name=Customer.first_name,
                last_name=Customer.last_name,
                message=f"Your new password is {Customer.password}"
            )
        finally:
            print(f'Sending New Password to {Customer=}')
@dataclass
class ComposeSendersService(BaseSendersService):
    sender_services: Iterable[BaseSendersService]

    async def send_auth_code(self, Customer: CustomerEntity, auth_code: str) -> None:
        for service in self.sender_services:
            await service.send_auth_code(auth_code, Customer)

