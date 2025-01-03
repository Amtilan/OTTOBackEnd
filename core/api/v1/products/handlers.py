


from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.products.schemas import OutputProductAnalysisResult, ProductTakeSchema, RecieveAnalysisResult, RecieveMessage
from core.apps.common.exception import ServiceException
from core.apps.common.gemini import RecommendationGenerator
from core.apps.products.services import BaseProductsService, ProductsService
from core.core.containers import get_container


router=Router(tags=['Products'])




@router.post('take_product', response=ApiResponse[RecieveMessage], operation_id='take_product', auth=None)
async def take_product_handler(
    request: HttpRequest,
    schema: ProductTakeSchema,
) -> ApiResponse[RecieveMessage]:
    container = get_container()
    service: BaseProductsService = ProductsService()
    try:
        await service.send_produtcs(
            access_token=schema.access_token,
            products=schema.produtcs,
            cost=schema.cost,
        )
    except ServiceException as exception:
        raise HttpError(
            status_code=400,
            message=exception.message,
        ) from exception
    
    return ApiResponse(data=RecieveMessage(message='Products has sended to operator'))

@router.post('take_results', response=ApiResponse[OutputProductAnalysisResult], operation_id='take_results', auth=None)
def take_results(
    request: HttpRequest,
    schema: RecieveAnalysisResult,    
) -> ApiResponse[OutputProductAnalysisResult]:
    result = RecommendationGenerator(analysis_results=schema.result)
    return ApiResponse(data=OutputProductAnalysisResult(result=result.recommendations))