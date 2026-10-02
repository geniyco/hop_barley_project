from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView # Імпорти Swagger

urlpatterns = [
    # Адмін-панель Django
    path('admin/', admin.site.urls),

    # Підключаємо каталог товарів як головну сторінку сайту
    path('', include('products.urls', namespace='products')),
    path('', include('orders.urls', namespace='orders')),

    path('users/', include('users.urls', namespace='users')),

    # Ендпоінт для завантаження сирої схеми OpenAPI (YAML/JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Інтерактивна сторінка документації Swagger за адресою з ТЗ
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Дозволяємо Django відображати зображення товарів у режимі розробки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
