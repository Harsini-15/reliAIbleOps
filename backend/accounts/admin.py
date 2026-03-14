from django.contrib import admin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']
