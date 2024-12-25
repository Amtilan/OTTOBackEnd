

from core.apps.common.models import UserBaseModel
from django.db import models

from core.apps.customers.entities.customers import CustomerEntity

class Customer(UserBaseModel):
    password = models.CharField(
        verbose_name='Пароль',
        max_length=255,
    )
    is_confirmed = models.BooleanField(
        verbose_name="Подтвержден ли аккаунт",
        default=False
    )
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name

    def to_entity(self):
        return CustomerEntity(
            id=self.pk,
            first_name=self.first_name,
            last_name=self.last_name,
            created_at=self.created_at,
            phone_number=self.phone_number,
            email=self.email,
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            password=self.password,
        )
