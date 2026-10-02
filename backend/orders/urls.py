from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders'

# Реєструємо API маршрути замовлень з ТЗ
router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='api_orders')

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # НОВИЙ МАРШРУТ ДЛЯ ОФОРМЛЕННЯ ЗАМОВЛЕННЯ
    path('checkout/', views.order_create, name='checkout'),
    path('api/', include(router.urls)),
]