from django.db import models

from core.apps.common.models import TimeBaseModel
from core.apps.customers.entities.customers import CustomerEntity
from core.apps.pred_results.entity import Pred_resultsEntity

# Create your models here.

class Pred_results(TimeBaseModel):
    customer=models.ForeignKey(
        to='customers.Customer',
        verbose_name='Customer',
        related_name='Pred_results',
        on_delete=models.CASCADE,
    )
    severity=models.PositiveSmallIntegerField(
        verbose_name='Customer severity',
        default=1,
    )
    acne_count=models.PositiveSmallIntegerField(
        verbose_name="Customer's acne count",
        default=0,
    )
    @classmethod
    def from_entity(
        cls,
        pred_results: Pred_resultsEntity,
        customer: CustomerEntity,
    ) -> 'Pred_results':
        return cls(
            pk=pred_results.id,
            customer_id=customer.id,
            severity=pred_results.severity,
            acne_count=pred_results.acne_count,
        )
    def to_entity(self) -> Pred_resultsEntity:
        return Pred_resultsEntity(
            id=self.pk,
            severity=self.severity,
            acne_count=self.acne_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    class Meta:
        verbose_name='Prediction result'
        verbose_name_plural='Prediction results'
