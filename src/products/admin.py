from django.contrib import admin

from products.models import ReceivedMessage


class ReceivedMessageAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in ReceivedMessage._meta.fields if field.name != "is_already_read"]
    list_filter = ('is_already_read', 'datetime')


# Usage
admin.site.register(ReceivedMessage, ReceivedMessageAdmin)
