from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at")
    readonly_fields = ('thumbnail_url', 'video_480p', 'video_720p', 'video_1080p', 'video_4k')
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")
