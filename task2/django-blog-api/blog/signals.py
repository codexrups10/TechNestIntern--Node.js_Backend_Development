
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Post, Like, Comment


@receiver(post_save, sender=Post)
def update_post_published_date(sender, instance, created, **kwargs):
    """Set published_at when post status changes to published"""
    if instance.status == 'published' and not instance.published_at:
        instance.published_at = timezone.now()
        instance.save(update_fields=['published_at'])


@receiver([post_save, post_delete], sender=Like)
def update_post_likes_count(sender, instance, **kwargs):
    """Update post likes count when likes are added/removed"""
    post = instance.post
    post.likes_count = post.likes.count()
    post.save(update_fields=['likes_count'])


@receiver([post_save, post_delete], sender=Comment)
def update_comment_notification(sender, instance, created=False, **kwargs):
    """Handle comment notifications (placeholder for future implementation)"""
    if created:
        # Here you could send email notifications, push notifications, etc.
        pass
