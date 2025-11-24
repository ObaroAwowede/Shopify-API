from rest_framework import serializers #type: ignore
from decimal import Decimal
from .models import (
    User, Category, Product, ProductImage, 
    Address, Order, OrderItem, Cart, CartItem, Review
)
from django.db.models import Avg

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

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'price', 'stock', 
            'is_available', 'is_in_stock', 'category', 'category_id',
            'images', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    #below is the function to calculate the average of all reviews, or return 0 if there are none
    def get_average_rating(self, obj):
        result = obj.reviews.aggregate(Avg('rating'))
        return result['rating__avg'] or 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('The price of a product must be more than 0')
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock can not be negative')