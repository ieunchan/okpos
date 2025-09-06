from django.contrib import admin
from django.urls import path
from django.urls import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


swagger_schema_view = get_schema_view(
    openapi.Info(
        title="OKPOS Product API",
        default_version="v1",
        description="상품, 옵션, 태그 관리 API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny, ),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path(
        'doc/',
        swagger_schema_view.with_ui('swagger', cache_timeout=0),
        name='swagger_ui'
    ),
]
