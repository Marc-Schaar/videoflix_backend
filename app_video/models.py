import uuid
from django.db import models


def video_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}" 
    return f"videos/{uuid.uuid4()}/{filename}"




class Video(models.Model):
    title = models.CharField(max_length=250, null= False, blank=False)
    description= models.TextField(max_length=1000, null=False, blank=False)
    category = models.CharField(max_length=250, null=False, blank=False)
    video_file = models.FileField(upload_to=video_upload_path)
    thumbnail_url = models.ImageField(upload_to=video_upload_path )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
