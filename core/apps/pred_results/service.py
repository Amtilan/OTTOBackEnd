


from abc import abstractmethod
from dataclasses import dataclass

from core.apps.customers.entities.customers import CustomerEntity
from core.apps.pred_results.entity import Pred_resultsEntity
from core.apps.pred_results.models import Pred_results


@dataclass
class BasePredResults:
    @abstractmethod
    def save_pred_result(
        self,
        customer: CustomerEntity,
        predres: Pred_resultsEntity,
    ) -> Pred_resultsEntity:
        ...
    @abstractmethod        
    def get_pred_results(
        self, 
        customer: CustomerEntity
    ) -> list[Pred_resultsEntity]:
        ...

class ORMPredResults(BasePredResults):
    def save_pred_result(
        self,
        customer: CustomerEntity,
        predres: Pred_resultsEntity,
    ) -> Pred_resultsEntity:
        predresDTO: Pred_results = Pred_results.from_entity(
            pred_results=predres,
            customer=customer,
        )
        predresDTO.save()
        return predresDTO.to_entity()
    def get_pred_results(
        self, 
        customer: CustomerEntity
    ) -> list[Pred_resultsEntity]:
        predres_dtos = Pred_results.objects.filter(customer_id=customer.id)
        return [predres_dto.to_entity() for predres_dto in predres_dtos]
