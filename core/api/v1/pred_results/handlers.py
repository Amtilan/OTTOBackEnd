


from django.http import HttpRequest
from ninja import Router

from core.api.schemas import ApiResponse
from core.api.v1.pred_results.schemas import PredResultInSchema, PredResultOutSchema
from core.api.v1.pred_results.use_case import CreatePredResultUseCase
from core.core.containers import get_container


router = Router(tags=['Prediction Results'])

@router.post(
    '/prediction', 
    response=ApiResponse[PredResultOutSchema], 
    operation_id='create_prediction_result', 
    auth=None
)
def create_prediction_result(
    request: HttpRequest,
    access_token: str,
    pred_result: PredResultInSchema,
) -> ApiResponse[PredResultOutSchema]:
    container = get_container()
    use_case: CreatePredResultUseCase = container.resolve(CreatePredResultUseCase)
    result = use_case.execute(
        access_token=access_token,
        pred_res=pred_result.to_entity(),
    )
    return ApiResponse(
        data=PredResultOutSchema.from_entity(
            pred_results_entity=result
        ),
    )

@router.get(
    '/prediction',
    response=ApiResponse[list[PredResultOutSchema]], 
    operation_id='get_prediction_results', 
    auth=None
)
def get_all_predictions(
    request: HttpRequest,
    access_token: str,
) -> ApiResponse[list[PredResultOutSchema]]:
    container = get_container()
    use_case: CreatePredResultUseCase = container.resolve(CreatePredResultUseCase)
    result = use_case.get_all_pred_results(
        access_token=access_token,
    )
    return ApiResponse(
        data=[PredResultOutSchema.from_entity(pred_result_entity) for pred_result_entity in result],
    )   