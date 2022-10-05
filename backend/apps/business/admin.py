from django.contrib import admin

from .models import (
    Account,
    RequestCreateAccount,
    Replenishment,
    Transfer,
    Payment,
)


admin.site.register(Account)
admin.site.register(RequestCreateAccount)
admin.site.register(Replenishment)
admin.site.register(Transfer)
admin.site.register(Payment)