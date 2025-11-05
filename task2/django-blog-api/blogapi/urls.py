from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from blog.hello import hello  # Import the hello view

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Root-level hello endpoint
    path('hello/', hello),

    # JWT Authentication
    path('api/auth/', include([
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),

    # Main API routes
    path('api/v1/', include('blog.urls')),
]
