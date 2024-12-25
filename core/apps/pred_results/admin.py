from django.contrib import admin

from core.apps.pred_results.models import Pred_results

# Register your models here.
@admin.register(Pred_results)
class PredAdmin(admin.ModelAdmin):
    list_display=('id', 'customer') 
    list_select_related=(
        'customer',
    )