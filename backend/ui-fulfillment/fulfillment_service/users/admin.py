from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as ContribUserAdmin

from .models import User


class UserAdmin(ContribUserAdmin):
    model = User
    fieldsets = ContribUserAdmin.fieldsets + ((None, {'fields': ('ml_uuid',)}),)
    add_fieldsets = ContribUserAdmin.add_fieldsets + ((None, {'fields': ('ml_uuid',)}),)


admin.site.register(User, UserAdmin)
