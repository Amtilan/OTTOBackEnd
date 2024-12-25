from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError


from core.api.schemas import ApiResponse

from core.api.v1.customers.schemas import AuthInSchemaEmail, AuthInSchemaPhone, AuthOutSchema, ChangePasswordInSchema, ConfirmInSchema, CustomerPhoneInSchema, RegisterInSchema, AuthOutSchema, SendCodeSchema, TokenInSchema
from core.apps.common.exception import ServiceException
from core.apps.customers.services.auth import BaseAuthService
from core.core.containers import get_container


router=Router(tags=['Customers'])

@router.post('auth-email', response=ApiResponse[AuthOutSchema], operation_id='authorize_email', auth=None)
def authorize_handler(
    request: HttpRequest,
    schema: AuthInSchemaEmail,
) -> ApiResponse[AuthOutSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)
    customer=service.authorize_by_email(
        email=schema.email,
        password=schema.password,
    )
    return ApiResponse(data=AuthOutSchema(refresh_token=customer.refresh_token,access_token=customer.access_token,))

@router.post('auth-phone', response=ApiResponse[AuthOutSchema], operation_id='authorize_phone', auth=None)
def authorize_handler(
    request: HttpRequest,
    schema: AuthInSchemaPhone,
) -> ApiResponse[AuthOutSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)
    customer=service.authorize_by_phone_number(
        phone_number=schema.phone_number,
        password=schema.password,
        
    )
    return ApiResponse(data=AuthOutSchema(refresh_token=customer.refresh_token,access_token=customer.access_token,))



@router.post('register', response=ApiResponse[SendCodeSchema], operation_id='register', auth=None)
async def register_handler(
    request: HttpRequest,
    schema: RegisterInSchema,
) -> ApiResponse[SendCodeSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)
    await service.register(
        phone_number=schema.phone_number,
        email=schema.email,
        first_name=schema.first_name,
        last_name=schema.last_name,
        password=schema.password,
    )
    return ApiResponse(data=SendCodeSchema(message=f'Code sended to: {schema.phone_number}'))

@router.post('confirm', response=ApiResponse[AuthOutSchema], operation_id='confirmCode', auth=None)
def get_token_handler(request: HttpRequest, schema: ConfirmInSchema) -> ApiResponse[AuthOutSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)

    try:
        customer = service.confirm(code=schema.code, phone_number=schema.phone_number)
    except ServiceException as exception:
        raise HttpError(
            status_code=400,
            message=exception.message,
        ) from exception

    return ApiResponse(data=AuthOutSchema(refresh_token=customer.refresh_token, access_token=customer.access_token))

@router.post('get_new_token', response=ApiResponse[AuthOutSchema], operation_id='get_new_token', auth=None)
def get_new_token_handler(
    request: HttpRequest, 
    schema: TokenInSchema,
) -> ApiResponse[AuthOutSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)
    try:
        customer = service.refresh(refresh_token=schema.refresh_token)
    except ServiceException as exception:
        raise HttpError(
            status_code=400, 
            message=exception.message,
        ) from exception
    
    return ApiResponse(data=AuthOutSchema(refresh_token=customer.refresh_token, access_token=customer.access_token))

@router.patch(
    'change-password',
    response=ApiResponse[AuthOutSchema],
    operation_id='change-password',
    auth=None,
)
def change_password(
    request: HttpRequest,
    access_token: str,
    schema: ChangePasswordInSchema,
) -> ApiResponse[AuthOutSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)
    try:
        customer = service.change_password(
            access_token=access_token, 
            new_password=schema.new_password,
            password=schema.password
        )
    except ServiceException as exception:
        raise HttpError(
            status_code=400,
            message=exception.message,
        ) from exception
    
    return ApiResponse(data=AuthOutSchema(refresh_token=customer.refresh_token, access_token=customer.access_token))

@router.put(
    'reset_password',
    response=ApiResponse[SendCodeSchema],
    operation_id='reset-password',
    auth=None,
)
async def reset_password(
    request: HttpRequest,
    schema: CustomerPhoneInSchema,
) -> ApiResponse[SendCodeSchema]:
    container = get_container()
    service: BaseAuthService = container.resolve(BaseAuthService)
    await service.reset_password(phone_number=schema.phone_number)
    return ApiResponse(data=SendCodeSchema(message=f'Password sended to: {schema.phone_number}'))