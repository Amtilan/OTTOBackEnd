from typing import Optional
from ninja import Schema
from pydantic import EmailStr


class RegisterInSchema(Schema):
    phone_number: str
    email: Optional[EmailStr]
    first_name: str
    last_name: Optional[str] = ''
    password: str

class ChangePasswordInSchema(Schema):
    password: str
    new_password: str

class AuthInSchemaEmail(Schema):
    email: Optional[EmailStr]
    password: str

class AuthInSchemaPhone(Schema):
    phone_number: str
    password: str

class CustomerPhoneInSchema(Schema):
    phone_number: str

class AuthOutSchema(Schema):
    refresh_token: str
    access_token: str

class SendCodeSchema(Schema):
    message: str

class TokenCodeSchema(Schema):
    token: str

class TokenInSchema(Schema):
    refresh_token: str

    
class ConfirmInSchema(Schema):
    code: str
    phone_number: str