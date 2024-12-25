

from datetime import datetime
from pydantic import BaseModel

from core.apps.pred_results.entity import Pred_resultsEntity


class PredResultInSchema(BaseModel):
    acne_count: int
    severity: int
    
    def to_entity(self) -> Pred_resultsEntity:
        return Pred_resultsEntity(
            acne_count=self.acne_count,
            severity=self.severity,
        )
        

class CreatePredResultSchema(BaseModel):
    access_token: str
    pred_result: PredResultInSchema

class PredResultOutSchema(PredResultInSchema):
    id: int
    created_at: datetime
    updated_at: datetime | None
    
    @classmethod
    def from_entity(
        cls,
        pred_results_entity: Pred_resultsEntity,
    ) -> 'PredResultOutSchema':
        return cls(
            id=pred_results_entity.id,
            acne_count=pred_results_entity.acne_count,
            severity=pred_results_entity.severity,
            created_at=pred_results_entity.created_at,
            updated_at=pred_results_entity.updated_at,
        )
