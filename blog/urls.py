from django.urls import path
from .views import *

urlpatterns = [
    path('', BlogPostListCreateView.as_view(), name='blogpost-list-create'),
    path('<int:pk>/', BlogPostDetailView.as_view(), name='blogpost-detail'),  # Retrieve, update, delete a specific blog post

   
    path('api/blog/<int:blog_id>/', get_blog_post_by_id, name='get_blog_post_by_id'),
    
]
