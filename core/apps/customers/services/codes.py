

from abc import ABC, abstractmethod
import random
import string
from django.core.cache import cache
from core.apps.customers.entities.customers import CustomerEntity
from core.apps.customers.exception.codes import CodeNotEqual, CodeNotFoundException


class BaseCodeService(ABC):
    @abstractmethod
    def generate_auth_code(self, Customer: CustomerEntity) -> str:
        ...
    
    @abstractmethod
    def validate_auth_code(self, code: str, Customer: CustomerEntity) -> None:        
        ...
        
class DjangoCacheCodeService(BaseCodeService):
    def generate_auth_code(self, Customer: CustomerEntity) -> str:
        auth_code = ''.join(random.choices(string.digits, k=6))
        cache.set(Customer.phone_number, auth_code)
        return auth_code
    
    def validate_auth_code(self, code: str, Customer: CustomerEntity) -> None:
        cache_code = cache.get(Customer.phone_number, code)

        if cache_code is None:
            raise CodeNotFoundException(code=code)
        if cache_code != code:
            raise CodeNotEqual(code=code, cached_code=cache_code, Customer_phone_number=Customer.phone_number)

        cache.delete(Customer.phone_number)