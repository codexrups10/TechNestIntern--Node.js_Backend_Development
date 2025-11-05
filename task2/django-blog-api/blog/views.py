
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import Post, Category, Tag, Comment, Like
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CategorySerializer, TagSerializer, CommentSerializer, LikeSerializer,
    PostStatsSerializer, UserStatsSerializer
)
from .permissions import IsOwnerOrReadOnly, IsPostOwnerOrReadOnly
from .filters import PostFilter

User = get_user_model()
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""

    queryset = User.objects.all().select_related().prefetch_related('posts')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'username', 'email']
    ordering = ['-created_at']

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get user's posts"""
        user = self.get_object()
        posts = user.posts.all().select_related('category', 'author').prefetch_related('tags')

        # Apply filtering
        status_filter = request.query_params.get('status')
        if status_filter:
            posts = posts.filter(status=status_filter)

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blog posts"""

    queryset = Post.objects.all().select_related('author', 'category').prefetch_related('tags', 'comments', 'likes')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'author__username', 'category__name']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'likes_count', 'published_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsPostOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = self.queryset

        # Anonymous users can only see published posts
        if not self.request.user.is_authenticated:
            return queryset.filter(status='published')

        # Authenticated users can see their own posts + published posts
        if self.action == 'list':
            return queryset.filter(
                Q(status='published') | Q(author=self.request.user)
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Retrieve post and increment view count"""
        instance = self.get_object()

        # Increment view count only for published posts
        if instance.status == 'published':
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like/unlike a post"""
        post = self.get_object()
        user = request.user

        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
            # Update like count
            post.likes_count = post.likes.count()
            post.save(update_fields=['likes_count'])
            return Response({'message': 'Post unliked'})
        else:
            # Update like count
            post.likes_count = post.likes.count()
            post.save(update_fields=['likes_count'])
            serializer = LikeSerializer(like, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts"""
        posts = self.get_queryset().filter(is_featured=True, status='published')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular posts (most viewed)"""
        posts = self.get_queryset().filter(status='published').order_by('-views_count')[:10]
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending posts (most liked in last 7 days)"""
        week_ago = timezone.now() - timezone.timedelta(days=7)
        posts = self.get_queryset().filter(
            status='published',
            created_at__gte=week_ago
        ).order_by('-likes_count')[:10]

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        """Get current user's posts"""
        posts = Post.objects.filter(author=request.user).select_related('category').prefetch_related('tags')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing categories"""

    queryset = Category.objects.all().annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    )
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'post_count']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get posts in category"""
        category = self.get_object()
        posts = category.posts.filter(status='published').select_related('author').prefetch_related('tags')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tags"""

    queryset = Tag.objects.all().annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    )
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'post_count']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get posts with tag"""
        tag = self.get_object()
        posts = tag.posts.filter(status='published').select_related('author', 'category').prefetch_related('tags')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""

    queryset = Comment.objects.all().select_related('author', 'post').prefetch_related('replies')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'is_approved']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Set author when creating comment"""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get replies to a comment"""
        comment = self.get_object()
        replies = comment.replies.filter(is_approved=True).select_related('author')
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)


# Analytics ViewSet
class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics and statistics"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def post_stats(self, request):
        """Get post statistics"""
        stats = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.objects.filter(status='published').count(),
            'draft_posts': Post.objects.filter(status='draft').count(),
            'total_views': Post.objects.aggregate(
                total=models.Sum('views_count')
            )['total'] or 0,
            'total_likes': Like.objects.count(),
            'total_comments': Comment.objects.filter(is_approved=True).count(),
        }

        serializer = PostStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """Get user statistics"""
        week_ago = timezone.now() - timezone.timedelta(days=7)

        stats = {
            'total_users': User.objects.count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'active_users': User.objects.filter(
                last_login__gte=week_ago
            ).count(),
        }

        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
