from rest_framework import serializers
from .models import Product, Category, Review

class CategorySerializer(serializers.ModelSerializer):
    """Серіалізатор для категорій товарів."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


class ProductSerializer(serializers.ModelSerializer):
    """Серіалізатор для списку товарів (використовується в API каталогу)."""
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'slug', 'description', 'price', 'image', 'is_active', 'stock']


class ReviewSerializer(serializers.ModelSerializer):
    """Серіалізатор для відгуків до товарів."""
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']