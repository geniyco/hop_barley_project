from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from typing import Any

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для реєстрації користувачів через REST API згідно з ТЗ 3.7.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'phone', 'shipping_address']

    def create(self, validated_data: dict) -> Any:  # Змінили тип повернення на Any для сумісності з dynamic model
        # Безпечне створення користувача із хешуванням пароля
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            shipping_address=validated_data.get('shipping_address', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user