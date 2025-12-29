from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role_id', 'phone', 'created_at']
    list_filter = ['role_id']
    search_fields = ['user__username', 'user__email']