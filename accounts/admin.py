from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.
# admin.site.register(User, UserAdmin)#djando default UserAdmin

# Customize UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
    )
