

from abc import ABC, abstractmethod 
from dataclasses import dataclass

from core.apps.common.telethon.service import TelegramConfig, TelegramService
from core.apps.customers.entities.customers import CustomerEntity
from core.apps.customers.services.customers import BaseCustomerService, ORMCustomerService

@dataclass
class BaseProductsService(ABC):
    @abstractmethod
    async def send_products(self, access_token: str, products: list[str], cost: int) -> None:
        ...
        
@dataclass
class ProductsService(BaseProductsService):
    tgsend: TelegramService = TelegramService(config=TelegramConfig)
    customer_serv: BaseCustomerService = ORMCustomerService()

    async def send_products(self, access_token: str, products: list[str], cost: int) -> None:
        customer: CustomerEntity = await self.customer_serv.get_Customer_by_access_token(
            access_token=access_token
        )
        await self.tgsend.send_products(
            customer=customer,
            products=products,
            cost=cost
        )