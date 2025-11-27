from django.urls import path, include
from rest_framework.routers import DefaultRouter # type: ignore
from .views import (
    UserRegisterView,
    UserViewSet,
    ProductImageViewset,
    ProductViewSet,
    CategoryViewSet,
    CartViewSet,
    ReviewViewSet,
    OrderViewSet,
    AddressViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'produts', ProductViewSet, basename='product')
router.register(r'product-images', ProductImageViewset, basename='productimage')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register-view'),
    path('', include(router.urls)),
]