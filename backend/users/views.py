from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model  # Додано get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from typing import Any

from .forms import UserRegisterForm, UserLoginForm
from .serializers import UserRegisterSerializer
from orders.models import Order


# ==========================================
# 1. ВЕБ-ІНТЕРФЕЙС (Django Templates & Sessions)
# ==========================================

def register_view(request: HttpRequest) -> HttpResponse:
    """Обробник для реєстрації нових користувачів через браузер."""
    if request.user.is_authenticated:
        return redirect('users:account')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Реєстрація успішна! Вітаємо, {user.username}!")
            return redirect('users:account')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    """Обробник для входу в систему через браузер."""
    if request.user.is_authenticated:
        return redirect('users:account')

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Раді бачити вас знову, {user.username}!")
            return redirect('users:account')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


@login_required(login_url='users:login')
def logout_view(request: HttpRequest) -> HttpResponse:
    """Обробник для виходу з акаунту."""
    logout(request)
    messages.success(request, "Ви успішно вийшли з акаунту.")
    return redirect('products:product_list')


@login_required(login_url='users:login')
def account_view(request: HttpRequest) -> HttpResponse:
    """Відображення Особистого кабінету та історії замовлень."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')

    context: dict[str, Any] = {
        'user': request.user,
        'orders': orders
    }
    return render(request, 'account.html', context)


# ==========================================
# 2. REST API АВТЕНТИФІКАЦІЯ
# ==========================================

class UserRegisterAPIView(generics.CreateAPIView):
    """
    API ендпоінт для реєстрації нових користувачів (/api/users/register/) з ТЗ [3.7].
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]