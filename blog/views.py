from django.shortcuts import render

# Create your views here.

from rest_framework import generics, permissions
from .models import BlogPost
from .serializers import BlogPostSerializer

class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
   

    def get_queryset(self):
        return BlogPost.objects.filter(created_by=self.request.user)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost  # Adjust the import based on your app structure
from .serializers import BlogPostSerializer  # Adjust the import based on your app structure

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Optionally make it accessible only to authenticated users
def get_blog_post_by_id(request, blog_id):
    try:
        blog_post = BlogPost.objects.get(id=blog_id)
    except BlogPost.DoesNotExist:
        return Response({"detail": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BlogPostSerializer(blog_post)
    return Response(serializer.data)
