from django.contrib import admin

from accounts.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'customer_type')


# Usage
admin.site.register(Customer, CustomerAdmin)
