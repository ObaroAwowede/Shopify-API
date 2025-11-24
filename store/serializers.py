from rest_framework import serializers #type: ignore
from decimal import Decimal
from .models import (
    User, Category, Product, ProductImage, 
    Address, Order, OrderItem, Cart, CartItem, Review
)

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 7)
    password_confirmed = serializers.CharField(write_only = True, min_length = 7)
    class Meta:
        model = User
        fields = ('username','email', 'first_name', 'last_name', 'password', 'password_confirmed')
    
    def validate(self, data):
        if data['password'] != data['password_confirmed']:
            raise serializers.ValidationError('Passwords do not macth')
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirmed')
        user = User.objects.create_user(**validated_data)
        return user
    
class CategorySerializer(serializers.ModelSerializer):
    product_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'product_total', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_product_total(self, obj):
        return obj.products.filter(is_available=True).count()
    
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'created_at')
        read_only_fields = ('id','created_at')