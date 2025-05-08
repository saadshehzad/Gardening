from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from users.models import User
from .models import *
from .serializers import *

class PostListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = UserPost.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            description = request.data.get("description")
            image = request.FILES.get('image')
            if not image:
                return Response({"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                post = Post.objects.create(description=description, image=image)
                UserPost.objects.create(post=post, user=request.user)
                return Response(
                    {"message": "Post created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"message": f"Error while creating Post: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        post_id = request.data.get("post_id")
        if not post_id:
            return Response({"error": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_post = UserPost.objects.get(id=post_id, user=request.user)
            user_post.delete()
            return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except UserPost.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class ArticlesListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer
    queryset = Articles.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            image = request.FILES.get("image")
            if not image:
                return Response({"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                Articles.objects.create(
                    image=image,
                    url=serializer.validated_data["url"],
                    title=serializer.validated_data["title"],
                    user_name=request.user.username
                )
                return Response(
                    {"message": "Article created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"message": f"Error while creating article: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportProblemListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportProblemSerializer
    queryset = ReportProblem.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        images = request.FILES.getlist("image")
        image_urls = []
        for image in images:
            try:
                path = default_storage.save(f"images/{image.name}", ContentFile(image.read()))
                relative_url = default_storage.url(path)
                full_url = request.build_absolute_uri(relative_url)
                image_urls.append(full_url)
            except Exception as e:
                return Response({"error": f"Failed to save image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data["image"] = json.dumps(image_urls) if image_urls else None
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(
                {"message": "Report Problem created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPostLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        user_post_likes = UserPostLike.objects.filter(user_post=user_post).values_list('liked_by__username', flat=True)
        return Response({"likes": list(user_post_likes)}, status=status.HTTP_200_OK)
    def post(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        user_post_like, created = UserPostLike.objects.get_or_create(
            user_post=user_post, liked_by=request.user
        )
        if created:
            return Response({"detail": "Post liked successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_post_like = UserPostLike.objects.get(user_post=user_post, liked_by=request.user)
            user_post_like.delete()
            return Response({"detail": "You have removed the like successfully"}, status=status.HTTP_204_NO_CONTENT)
        except UserPostLike.DoesNotExist:
            return Response({"error": "You have not liked this post"}, status=status.HTTP_400_BAD_REQUEST)

class UserPostShareAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        user_post_shares = UserPostShare.objects.filter(user_post=user_post).values_list('shared_by__username', flat=True)
        return Response({"shares": list(user_post_shares)}, status=status.HTTP_200_OK)
    
    def post(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        user_post_share, created = UserPostShare.objects.get_or_create(
            user_post=user_post, shared_by=request.user
        )
        if created:
            return Response({"detail": "Post shared successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You have already shared this post"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_post_share = UserPostShare.objects.get(user_post=user_post, shared_by=request.user)
            user_post_share.delete()
            return Response({"detail": "You have removed the share successfully"}, status=status.HTTP_204_NO_CONTENT)
        except UserPostShare.DoesNotExist:
            return Response({"error": "You have not shared this post"}, status=status.HTTP_400_BAD_REQUEST)

class UserPostCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user_post = UserPost.objects.get(pk=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        comments_qs = UserPostComment.objects.filter(user_post=user_post).select_related('comment_by')

        comments_data = [
            {
                "id": comment.id,
                "name": comment.comment_by.username,
                "comment": comment.comment,
                "timestamp": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for comment in comments_qs
        ]

        return Response({"comments": comments_data}, status=status.HTTP_200_OK)
    
    def post(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        comment_text = request.data.get("comment")
        if not comment_text:
            return Response({"error": "Comment text is required"}, status=status.HTTP_400_BAD_REQUEST)

        user_post_comment = UserPostComment.objects.create(
            user_post=user_post, comment_by=request.user, comment=comment_text
        )
        return Response(
            {
                "message": "Comment added successfully",
                "comment_id": user_post_comment.id
            },
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        try:
            user_post = UserPost.objects.get(id=pk)
        except UserPost.DoesNotExist:
            return Response({"error": "User post not found"}, status=status.HTTP_404_NOT_FOUND)

        comment_id = request.data.get("comment_id")
        if not comment_id:
            return Response({"error": "Comment ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment_id = int(comment_id)  
        except (ValueError, TypeError):
            return Response({"error": "Comment ID must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_post_comment = UserPostComment.objects.get(
                id=comment_id, user_post=user_post, comment_by=request.user
            )
            user_post_comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except UserPostComment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)