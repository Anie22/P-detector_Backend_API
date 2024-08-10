from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import *
from django.utils.html import format_html


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

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'pic')
    fieldsets = ()

    add_fieldsets=(
        (None, {
            'classes':('wide'),
            'fields':('user', 'pic')
        }),
    )

    def Image(self, obj):
        return format_html('<img src="{}" style="max-width:90px; max-height:90px"/>'.format(obj.image.url))

admin.site.register(User, MyUserAdmin)
admin.site.register(OneTimeCode)
admin.site.register(UserProfile, ProfileAdmin)