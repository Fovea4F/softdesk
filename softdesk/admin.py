from django.contrib import admin
from softdesk.models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'password', 'first_name', 'last_name', 'birthday')


admin.site.register(CustomUser, CustomUserAdmin)
