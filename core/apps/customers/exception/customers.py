from dataclasses import dataclass

from core.apps.common.exception import ServiceException


@dataclass(eq=True)
class CustomerTokenNotFoundException(ServiceException):
    token: str
    @property
    def message(self):
        return f"Customer {self.token=} not found"

@dataclass(eq=True)
class CustomerPasswordNotCorrectException(ServiceException):
    password: str
    @property
    def message(self):
        return f"Customer {self.password=} not correct"
@dataclass(eq=True)
class CustomerEmailNotFoundException(ServiceException):
    email: str
    @property
    def message(self):
        return f"Customer {self.email=} not correct"
@dataclass(eq=True)
class CustomerNotConfirmedException(ServiceException):
    @property
    def message(self):
        return f"Customer not confirmed"


@dataclass(eq=True)
class CustomerPhoneNumNotFoundException(ServiceException):
    phone_number: str
    @property
    def message(self):
        return f'Customer {self.phone_number=} not correct'

@dataclass(eq=True)
class CustomerExists(ServiceException):
    @property
    def message(self):
        return f"Customer already exists."
    
@dataclass(eq=True)
class CustomerEmailExists(ServiceException):
    email: str
    @property
    def message(self):
        return f"Customer with email {self.email} already exists."
    
@dataclass(eq=True)
class CustomerPhoneNumberExists(ServiceException):
    phone_number: str
    @property
    def message(self):
        return f"Customer with phone_number {self.phone_number} already exists."