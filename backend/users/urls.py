from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_view, name='account'),

    # ----------------==========================
    # 2. REST API АВТЕНТИФІКАЦІЯ (SimpleJWT)
    # ----------------==========================
    # Створення акаунту через POST-запит (Пункт 3.7 ТЗ)
    path('api/users/register/', views.UserRegisterAPIView.as_view(), name='api_register'),

    # Отримання access та refresh токенів при логіні (Пункт 3.7 ТЗ)
    path('api/users/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Оновлення access токену через refresh токен (Пункт 3.7 ТЗ)
    path('api/users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]