from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('',include(router.urls))
]