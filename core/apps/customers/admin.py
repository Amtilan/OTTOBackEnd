from django.contrib import admin

from core.apps.customers.models.customers import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=('id', 'first_name', 'last_name', 'password', 'phone_number')