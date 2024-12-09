from functools import lru_cache
import punq

from core.apps.customers.services.auth import AuthService, BaseAuthService
from core.apps.customers.services.codes import BaseCodeService, DjangoCacheCodeService
from core.apps.customers.services.customers import BaseCustomerService, ORMCustomerService
from core.apps.customers.services.sender import BaseSendersService, ComposeSendersService, EmailSendersService, PushSendersService, TGSenderService
from core.apps.customers.services.token import BaseJWTService, ORMJWTService

@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()
    
def _initialize_container() -> punq.Container:
    container=punq.Container()
    container.register(BaseCustomerService, ORMCustomerService)
    container.register(BaseCodeService, DjangoCacheCodeService)
    container.register(
        BaseSendersService, ComposeSendersService, sender_services=(
        # PushSendersService(), 
        # EmailSendersService(),
        TGSenderService(),
        ),
    )
    container.register(BaseAuthService, AuthService)
    
    
    return container