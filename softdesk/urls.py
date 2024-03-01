from django.urls import path, include
from rest_framework import routers

from .views1 import CustomUserViewSet

router = routers.SimpleRouter()
#router.register('user', CustomUserViewSet, basename='user')

urlpatterns = [
    path('user', CustomUserViewSet.as_view({'get': 'list'})),
]
