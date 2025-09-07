from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().prefetch_related("option_set", "tag_set")