from django.urls import path

from .views import CustomUserViewSetNew

urlpatterns = [
    path('', CustomUserViewSetNew),
    ]
