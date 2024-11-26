from django.contrib import admin
from .models import ModelUserProfile

@admin.register(ModelUserProfile)
class ModelUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin', 'is_participant')
    search_fields = ('user__username',)
    list_filter = ('is_admin', 'is_participant')