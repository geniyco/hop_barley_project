from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from typing import Any

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    """Форма реєстрації нового користувача на основі кастомної моделі з ТЗ."""
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(required=False, label="Телефон")
    shipping_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Адреса доставки за замовчуванням"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone', 'shipping_address')


class UserLoginForm(AuthenticationForm):
    """Форма входу користувача в систему."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Введіть логін'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Введіть пароль'
    }))