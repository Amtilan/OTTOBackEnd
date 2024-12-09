

from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.apps.customers.entities.customers import CustomerEntity
from core.apps.customers.services.codes import BaseCodeService
from core.apps.customers.services.customers import BaseCustomerService
from core.apps.customers.services.sender import BaseSendersService, TGSenderService


@dataclass(eq=False)
class BaseAuthService(ABC):
    Customer_service: BaseCustomerService
    codes_service: BaseCodeService
    sender_service: BaseSendersService
    
    @abstractmethod
    def authorize_by_phone_number(self, phone_number: str, password: str) -> CustomerEntity:
        ...
        
    @abstractmethod
    def authorize_by_email(self, email: str, password: str) -> CustomerEntity:
        ...
        
    @abstractmethod
    async def register(self, phone_number: str, email: str, first_name: str, last_name: str, password: str) -> None:
        ...
        
    @abstractmethod
    def refresh(self, refresh_token: str) -> CustomerEntity:
        ...
    
    @abstractmethod
    def confirm(self, code: str, phone_number: str) -> CustomerEntity:
        ...
        
        
class AuthService(BaseAuthService):
    def authorize_by_phone_number(self, phone_number: str, password: str) -> CustomerEntity:
        Customer = self.Customer_service.authorize_Customer_phone_num(
            phone_number=phone_number,
            password=password
        )
        return Customer
    
    def authorize_by_email(self, email: str, password: str) -> CustomerEntity:
        Customer=self.Customer_service.authorize_Customer_email(
            email=email,
            password=password,
        )
        return Customer
    
    async def register(self, phone_number: str,email: str, first_name: str, last_name: str, password: str) -> None:
        Customer= await self.Customer_service.create_Customer(
            phone_number=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        code=self.codes_service.generate_auth_code(Customer=Customer)
        sender: BaseSendersService = TGSenderService()
        await sender.send_auth_code(Customer=Customer, auth_code=code)

    def refresh(self, refresh_token: str) -> CustomerEntity:
        return self.Customer_service.get_new_by_refresh(refresh_token=refresh_token)
        
    def confirm(self, code: str, phone_number: str) -> CustomerEntity:
        Customer=self.Customer_service.get_Customer_by_phone_num(phone_number=phone_number)
        self.codes_service.validate_auth_code(code=code, Customer=Customer)
        self.Customer_service.get_confirmed(customer=Customer)
        return Customer