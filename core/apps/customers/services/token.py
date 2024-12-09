from ninja_jwt.tokens import RefreshToken
from abc import ABC, abstractmethod

from core.apps.customers.models.customers import Customer


class BaseJWTService(ABC):
    @abstractmethod
    def get_tokens_for_Customer(self, Customer: Customer) -> dict[str]:
        ...

class ORMJWTService(BaseJWTService):
    def get_tokens_for_Customer(self, Customer: Customer) -> dict[str]:
        refresh = RefreshToken.for_user(user=Customer)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
