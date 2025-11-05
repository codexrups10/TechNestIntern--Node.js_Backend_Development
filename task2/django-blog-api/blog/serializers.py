
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Category, Tag, Comment, Like

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'bio', 'location', 'birth_date'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""

    full_name = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'location', 'birth_date', 'avatar',
            'is_verified', 'post_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category model"""

    post_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag model"""

    post_count = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comment model"""

    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    is_reply = serializers.ReadOnlyField()
    replies_count = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'author_id', 'parent', 'is_reply',
            'replies_count', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set author from request user if not provided
        if 'author_id' not in validated_data:
            validated_data['author'] = self.context['request'].user
        else:
            validated_data['author_id'] = validated_data.pop('author_id')
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view (minimal fields)"""

    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category', 'tags',
            'status', 'featured_image', 'is_featured', 'views_count',
            'likes_count', 'reading_time', 'comments_count', 'published_at',
            'created_at', 'updated_at'
        ]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for post detail view (all fields)"""

    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'category',
            'tags', 'comments', 'status', 'featured_image', 'is_featured',
            'views_count', 'likes_count', 'reading_time', 'is_liked',
            'published_at', 'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Like.objects.filter(user=user, post=obj).exists()
        return False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating posts"""

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'category',
            'tag_ids', 'status', 'featured_image', 'is_featured', 'published_at'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        post = Post.objects.create(**validated_data)
        if tag_ids:
            post.tags.set(tag_ids)
        return post

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tag_ids is not None:
            instance.tags.set(tag_ids)

        return instance


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for like model"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Stats serializers for analytics
class PostStatsSerializer(serializers.Serializer):
    """Serializer for post statistics"""

    total_posts = serializers.IntegerField()
    published_posts = serializers.IntegerField()
    draft_posts = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""

    total_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
