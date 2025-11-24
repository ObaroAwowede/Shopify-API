from rest_framework import serializers #type: ignore
from decimal import Decimal
from .models import (
    User, Category, Product, ProductImage, 
    Address, Order, OrderItem, Cart, CartItem, Review
)
from django.db.models import Avg

class UserSerializer(serializers.ModelSerializer):
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
            raise serializers.ValidationError('Passwords do not match')
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
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock can not be negative')
        return value
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'full_name', 'phone_number', 'full_address',
            'city', 'state', 'postal_code', 'country', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only = True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'subtotal')
        read_only_fields = ('id', 'price')
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be more than 0')
        return value
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemSerializer(many=True,write_only= True, source ='items')
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='shipping_address',
        write_only=True
    )
    billing_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='billing_address',
        write_only=True,
        required=False
    )
    user_info = UserSerializer(source='user',read_only=True)
    item_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user_info', 'shipping_address', 
            'billing_address', 'shipping_address_id', 'billing_address_id',
            'order_status', 'payment_status', 'subtotal', 'shipping_cost', 
            'total', 'notes', 'items', 'items_data', 'item_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'order_number', 'subtotal', 'total', 'created_at', 'updated_at')
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def validate_items_data(self, value):
        if not value:
            raise serializers.ValidationError('Order must include at least one item')
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        #below i'm calculating the subtotal
        subtotal = Decimal('0.00')
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            
            #checking if stock quantity ordered is available
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}, Available: {product.stock}"
                )
                
            subtotal = subtotal + (product.price * quantity)
        
        #calculating total price
        shipping_cost = validated_data.get('shipping_cost', Decimal('0.00'))
        total = subtotal + shipping_cost
        
        #using shipping_address if billing_address is not given
        if 'billing_address' not in validated_data:
            validated_data['billing_address'] = validated_data['shipping_address']
        
        #creating the order
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            total=total,
            **validated_data
        )
        
        #creating the order items and updating stock
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
                        
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            
            product.stock = product.stock - quantity
            product.save()
        return order
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        
        if product and quantity:
            if not product.is_available:
                raise serializers.ValidationError("This product is not available.")
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock. Available: {product.stock}"
                )
        
        return data 
   
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')