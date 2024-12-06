from dataclasses import dataclass

from core.apps.common.exception import ServiceException


@dataclass(eq=False)
class CodeException(ServiceException):
    @property
    def message(self):
        return "Auth code exception associated"
    
@dataclass(eq=False)
class CodeNotFoundException(CodeException):
    code: str
    @property
    def message(self):
        return "Code not found"
    
@dataclass(eq=False)
class CodeNotEqual(CodeException):
    code: str
    cached_code: str
    Customer_phone_number: str
    
    @property
    def message(self):
        return "Auth code not equal exception associated"