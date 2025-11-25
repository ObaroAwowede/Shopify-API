from django.shortcuts import render  # type: ignore
from rest_framework import generics, permissions, status, viewsets, filters # type: ignore
from rest_framework.decorators import action # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import UserRegistrationSerializer, UserSerializer, CategorySerializer, ProductSerializer, ReviewSerializer, ProductImageSerializer,AddressSerializer
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
    permissions = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ResultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['name', 'description']
    search_fields = ['name', 'created_at']
    ordering = ['name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permissions = [permissions.IsAuthenticatedOrReadOnly]
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
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
