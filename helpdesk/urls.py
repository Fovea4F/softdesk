"""
URL configuration for helpdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import SimpleRouter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from softdesk.views import CustomUserViewSet, ProjectViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="softdesk API",
        default_version='v1',
        description="Softdesk, gestion d'incidents",
        contact=openapi.Contact(email="tests@test.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    # The `permission_classes=(permissions.AllowAny,)` is specifying the permission classes for the
    # schema view. In this case, it is allowing any user to access the schema view without any
    # authentication or permission checks. This means that anyone can view the API documentation
    # provided by the schema view.
    permission_classes=(permissions.AllowAny,),
)

router = SimpleRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('project', ProjectViewSet, basename='project')
# router.register('project_create', ProjectCreateViewSet, basename='project-create')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api_auth', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
