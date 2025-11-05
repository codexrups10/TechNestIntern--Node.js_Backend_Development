
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Post, Category, Tag, Comment, Like


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""

    list_display = ['username', 'email', 'first_name', 'last_name', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'location', 'birth_date', 'avatar', 'is_verified')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""

    list_display = ['name', 'slug', 'post_count_admin', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def post_count_admin(self, obj):
        return obj.posts.count()
    post_count_admin.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model"""

    list_display = ['name', 'slug', 'post_count_admin', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def post_count_admin(self, obj):
        return obj.posts.count()
    post_count_admin.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model"""

    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views_count', 'likes_count', 'created_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    raw_id_fields = ['author', 'category']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('tags', 'status', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['views_count', 'likes_count']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model"""

    list_display = ['__str__', 'author', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    raw_id_fields = ['author', 'post', 'parent']
    ordering = ['-created_at']
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin configuration for Like model"""

    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    raw_id_fields = ['user', 'post']
    ordering = ['-created_at']
