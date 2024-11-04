from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'video', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']
