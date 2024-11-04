from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='courses/videos/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
