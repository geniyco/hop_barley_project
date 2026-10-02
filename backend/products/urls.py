from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductListView, ProductDetailView, ProductViewSet

app_name = 'products'

# Створюємо роутер для REST API
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api_products')

urlpatterns = [
    # Головна сторінка каталогу (прив'язуємо наш ListView)
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    path('api/', include(router.urls)),
]