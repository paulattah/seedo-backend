from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    video = models.FileField(upload_to='blog/videos/', null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

