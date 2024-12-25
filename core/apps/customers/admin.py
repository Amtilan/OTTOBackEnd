from django.contrib import admin

from core.apps.customers.models.customers import Customer
from core.apps.pred_results.models import Pred_results

class PredInline(admin.TabularInline):
    model=Pred_results
    extra=0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=('id', 'first_name', 'last_name', 'password', 'phone_number')
    inlines = (
        PredInline,
    )

