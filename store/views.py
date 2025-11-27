from django.shortcuts import render  # type: ignore
from rest_framework import generics, permissions, status, viewsets, filters # type: ignore
from rest_framework.decorators import action # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import UserRegistrationSerializer, UserSerializer, CategorySerializer, ProductSerializer, ReviewSerializer, ProductImageSerializer,AddressSerializer, OrderSerializer, CartSerializer
from .models import User, Category, Cart, CartItem, Product, ProductImage, Address, Order, OrderItem, Review
from rest_framework.pagination import PageNumberPagination # type: ignore
from django_filters.rest_framework import DjangoFilterBackend # type: ignore

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class ResultPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50
    
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 30

class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_token_for_user(user)
        return Response({
            'user': UserRegistrationSerializer(user, context={'request': request}).data,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        }, status=status.HTTP_201_CREATED)
        
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self,request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ResultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['name', 'description']
    search_fields = ['name', 'created_at']
    ordering = ['name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'category': ['exact'], #here i'm allowing users search for the exact category id
        'price': ['gte', 'lte', 'exact'], #there are three types of filters here for an exact, lesser or greater value of a price specified
        'is_available': ['exact'], #allows filtering by availability status
        'stock': ['gte', 'lte'], #allows filtering by stock quantity
    }
    
    ordering_fields = ['price','created_at','name','stock']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Custom filter to filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    # here i'm creating an endpoint 'featured', to return the 10 most recently added products
    def featured(self, request):
        featured_products = self.get_queryset().order_by('-created_at')[:10]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        # here i'm getting all the reviews for a specific product
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
class ProductImageViewset(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ResultPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['order_status', 'payment_status']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see their own orders
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    #here i'm creating a custom endpoint called cancel, accepting only PATCH requests
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        order = self.get_object()   
        if order.order_status == 'cancelled':
            return Response(
                {'message': 'Order is already cancelled.'},
                status=status.HTTP_200_OK
            )    
        if order.order_status in ['shipped', 'delivered']:
            return Response(
                {'error': 'You can not cancel an order that has been shipped or delivered.'},
                status=status.HTTP_400_BAD_REQUEST
            )       
        order.order_status = 'cancelled'
        order.save()
        
        # Restore cancelled order to the stock
        for item in order.items.all():
            item.product.stock = item.product.stock + item.quantity
            item.product.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Each user has only one cart
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    # Get current user's cart
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if product is available
        if not product.is_available:
            return Response(
                {'error': 'Product is not available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check stock
        if product.stock < quantity:
            return Response(
                {'error': f'Insufficient stock. Available: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Creating an ednpoint 'update_item' to change the quantity of an item in the cart
    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        # i included this try except block, to 
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if quantity <= 0:
            cart_item.delete()
        else:
            # Check stock
            if cart_item.product.stock < quantity:
                return Response(
                    {'error': f'Insufficient stock. Available: {cart_item.product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    #creating an endpoint to delete an item from the cart, using it's product_id
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    # creating an endpoint clear, accepting DELETE requests to delete every object in the cart
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ResultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Here i'm filtering reviews by product
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)