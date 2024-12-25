import secrets
from asgiref.sync import sync_to_async
from abc import ABC, abstractmethod
from django.db import transaction
from core.apps.customers.entities.customers import CustomerEntity
from core.apps.customers.exception.customers import CustomerAccessTokenNotTrue, CustomerEmailExists, CustomerEmailNotFoundException, CustomerNotConfirmedException, CustomerPasswordNotCorrectException, CustomerPhoneNumNotFoundException, CustomerPhoneNumberExists, CustomerTokenNotFoundException
from core.apps.customers.models.customers import Customer
from core.apps.customers.services.token import BaseJWTService, ORMJWTService


class BaseCustomerService(ABC):
    @abstractmethod
    async def create_Customer(self, phone_number: str ,email: str, first_name: str, last_name: str, password: str) -> CustomerEntity:
        ...
    @abstractmethod
    def delete_Customer(self, phone_number: str) -> None:
        ...
    @abstractmethod
    def generate_token(self, Customer_dto: Customer) -> CustomerEntity:
        ...
     
    @abstractmethod
    def authorize_Customer_email(self, email: str, password: str) -> CustomerEntity:
        ...
        
    @abstractmethod
    def authorize_Customer_phone_num(self, phone_number: str, password: str) -> CustomerEntity:
        ...
        
    @abstractmethod
    def get_Customer_by_email(self, email: str) -> CustomerEntity:
        ...
    
    @abstractmethod
    def get_Customer_by_phone_num(self, phone_number: str) -> CustomerEntity:
        ...
    @abstractmethod
    async def get_Customer_by_access_token(self, access_token: str) -> CustomerEntity:
        ...
    @abstractmethod
    def get_new_by_refresh(self, refresh_token: str) -> CustomerEntity:
        ...
    
    @abstractmethod
    def get_by_token(self, token: str) -> CustomerEntity:
        ...
        
    @abstractmethod
    def get_confirmed(self, customer: CustomerEntity) -> None:
        ...
    @abstractmethod
    def change_password(self, customer: CustomerEntity, new_password: str, password: str) -> None:
        ...
    @abstractmethod
    async def async_get_Customer_by_phone_num(self, phone_number: str) -> CustomerEntity:
        ...
    @abstractmethod
    async def async_reset_password(self, phone_number: str) -> CustomerEntity:
        ...


class ORMCustomerService(BaseCustomerService):
    JWT_service: BaseJWTService = ORMJWTService()
    async def create_Customer(self, phone_number: str, email: str, first_name: str, last_name: str, password: str) -> CustomerEntity:
        existing_email_customer = await sync_to_async(Customer.objects.filter(email=email).first)()
        if existing_email_customer:
            if not existing_email_customer.is_confirmed:
                await sync_to_async(self.delete_Customer)(phone_number=existing_email_customer.phone_number)
            else:
                raise CustomerEmailExists(email=email)

        existing_phone_customer = await sync_to_async(Customer.objects.filter(phone_number=phone_number).first)()
        if existing_phone_customer:
            if not existing_phone_customer.is_confirmed:
                await sync_to_async(self.delete_Customer)(phone_number=phone_number)
            else:
                raise CustomerPhoneNumberExists(phone_number=phone_number)

        @sync_to_async
        @transaction.atomic
        def create_customer():
            return Customer.objects.create(
                phone_number=phone_number,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )

        Customer_dto = await create_customer()

        return Customer_dto.to_entity()
    
    def delete_Customer(self, phone_number: str) -> None:
        customer_dto = Customer.objects.get(phone_number=phone_number)
        customer_dto.delete()
        
    def get_Customer_by_email(self, email: str) -> CustomerEntity:
        try:
            Customer_dto = Customer.objects.get(email=email)
            if not Customer_dto.is_confirmed:
                raise CustomerNotConfirmedException()
        except Customer.DoesNotExist:
            raise CustomerEmailNotFoundException(email=email)
        
        return self.generate_token(Customer_dto=Customer_dto)

    def get_Customer_by_phone_num(self, phone_number) -> CustomerEntity:
        try:
            Customer_dto = Customer.objects.get(phone_number=phone_number)
        except Customer.DoesNotExist:
            raise CustomerPhoneNumNotFoundException(phone_number=phone_number)
        
        return self.generate_token(Customer_dto=Customer_dto)
    
    async def get_Customer_by_access_token(self, access_token: str) -> CustomerEntity:
        customer_dto = await sync_to_async(Customer.objects.filter(access_token=access_token).first)()
        if not customer_dto:
            raise CustomerAccessTokenNotTrue("Access token is not valid.")
        return customer_dto.to_entity()

    def authorize_Customer_email(self, email: str, password: str) -> CustomerEntity:
        try:
            Customer_dto = Customer.objects.get(email=email)
            if Customer_dto.password != password:
                raise CustomerPasswordNotCorrectException(password=password)
            if not Customer_dto.is_confirmed:
                raise CustomerNotConfirmedException()
        except Customer.DoesNotExist:
            raise CustomerEmailNotFoundException(email=email)

        return self.generate_token(Customer_dto=Customer_dto)

    def authorize_Customer_phone_num(self, phone_number: str, password: str) -> CustomerEntity:
        try:
            Customer_dto = Customer.objects.get(phone_number=phone_number)
            if Customer_dto.password != password:
                raise CustomerPasswordNotCorrectException(password=password)
            if not Customer_dto.is_confirmed:
                raise CustomerNotConfirmedException()
        except  Customer.DoesNotExist:
            raise CustomerPhoneNumNotFoundException(phone_number=phone_number)
        
        return self.generate_token(Customer_dto=Customer_dto)

    def generate_token(self, Customer_dto: Customer) -> CustomerEntity:
        token = self.JWT_service.get_tokens_for_Customer(Customer=Customer_dto)
        Customer_dto.access_token, Customer_dto.refresh_token = token['access'], token['refresh']
        Customer_dto.save()
        return Customer_dto.to_entity()

    def get_new_by_refresh(self, refresh_token: str) -> CustomerEntity:
        try: 
            Customer_dto=Customer.objects.get(refresh_token=refresh_token)
        except Customer.DoesNotExist:
            raise CustomerTokenNotFoundException(token=refresh_token)
        return self.generate_token(Customer_dto=Customer_dto)
    
    def get_by_token(self, token: str) -> CustomerEntity:
        try:
            Customer_dto = Customer.objects.get(access_token=token)
        except Customer.DoesNotExist:
            raise CustomerTokenNotFoundException(token=token)

        return Customer_dto.to_entity()
    
    def get_confirmed(self, customer: CustomerEntity) -> None:
        Customer_dto=Customer.objects.get(phone_number=customer.phone_number)
        Customer_dto.is_confirmed = True
        Customer_dto.save()
    
    def change_password(self, customer: CustomerEntity, new_password: str, password: str) -> None:
        try:
            Customer_dto = Customer.objects.get(phone_number=customer.phone_number)
            if Customer_dto.password != password:
                raise CustomerPasswordNotCorrectException(password=password)
            Customer_dto.password = new_password
            Customer_dto.save()
        except Customer.DoesNotExist:
            raise CustomerPhoneNumNotFoundException(phone_number=customer.phone_number)
    async def async_get_Customer_by_phone_num(self, phone_number: str) -> CustomerEntity:
        customer_dto = await sync_to_async(Customer.objects.filter(phone_number=phone_number).first)()
        if not customer_dto:
            raise CustomerPhoneNumNotFoundException(phone_number=phone_number)
        return customer_dto.to_entity()
    async def async_reset_password(self, phone_number: str) -> CustomerEntity:
        customer_dto = await sync_to_async(Customer.objects.filter(phone_number=phone_number).first)()
        if not customer_dto:
            raise CustomerPhoneNumNotFoundException(phone_number=phone_number)
        new_password = secrets.token_hex(8)
        customer_dto.password = new_password
        await sync_to_async(customer_dto.save)()
        return customer_dto.to_entity()