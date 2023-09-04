from django.contrib import admin
from .models import UserProfile, UploadedFile


# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_ops_user']


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'uploaded_at']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)
