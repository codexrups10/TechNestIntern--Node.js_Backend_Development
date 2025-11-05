
import django_filters
from django.db.models import Q
from .models import Post, Category, Tag


class PostFilter(django_filters.FilterSet):
    """Filter class for Post model"""

    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    status = django_filters.ChoiceFilter(choices=Post.STATUS_CHOICES)
    is_featured = django_filters.BooleanFilter()
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    published_from = django_filters.DateFilter(field_name='published_at', lookup_expr='gte')
    published_to = django_filters.DateFilter(field_name='published_at', lookup_expr='lte')

    # Custom search filter that searches across multiple fields
    search = django_filters.CharFilter(method='filter_search', label='Search')

    class Meta:
        model = Post
        fields = {
            'views_count': ['exact', 'gte', 'lte'],
            'likes_count': ['exact', 'gte', 'lte'],
        }

    def filter_search(self, queryset, name, value):
        """
        Custom search method that searches across title, content, and author username
        """
        return queryset.filter(
            Q(title__icontains=value) |
            Q(content__icontains=value) |
            Q(author__username__icontains=value) |
            Q(author__first_name__icontains=value) |
            Q(author__last_name__icontains=value)
        )
