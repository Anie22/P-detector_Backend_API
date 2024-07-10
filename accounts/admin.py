from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OneTimeCode


class MyUserAdmin(BaseUserAdmin):
    list_display = ('firstName', 'lastName', 'email', 'date_joined', 'is_admin', 'is_active', 'is_lecturer')
    search_fields = ('firstName', 'email')
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    list_filter=('last_login',)
    fieldsets = ()

    add_fieldsets=(
        (None, {
            'classes':('wide'),
            'fields':('firstName', 'lastName', 'userName', 'email', 'account_type', 'password1', 'password2')
        }),
    )

    ordering=('firstName',)

admin.site.register(User, MyUserAdmin)
admin.site.register(OneTimeCode)