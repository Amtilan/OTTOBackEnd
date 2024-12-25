

from dataclasses import dataclass

from core.apps.customers.services.customers import BaseCustomerService
from core.apps.pred_results.entity import Pred_resultsEntity
from core.apps.pred_results.service import BasePredResults


@dataclass
class CreatePredResultUseCase:
    pred_res_service: BasePredResults
    customer_service: BaseCustomerService
    
    def execute(
        self, 
        access_token: str,
        pred_res: Pred_resultsEntity,    
    ) -> Pred_resultsEntity:
        customer=self.customer_service.get_by_token(
            token=access_token,
        )
        saved_pred_results=self.pred_res_service.save_pred_result(
            customer=customer,
            predres=pred_res,
        )
        return saved_pred_results
    
    def get_all_pred_results(
        self,
        access_token: str,
    ) -> list[Pred_resultsEntity]:
        customer=self.customer_service.get_by_token(
            token=access_token,
        )
        return self.pred_res_service.get_pred_results(
            customer=customer,
        )