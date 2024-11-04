from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CourseCreateView.as_view(), name='course-create'),
    path('', CourseListCreateView.as_view(), name='course-list-create'), 
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),   # Retrieve, update, delete a specific course
    
]
