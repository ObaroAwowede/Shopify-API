from django.contrib import admin #type: ignore
from django.urls import path, include #type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # type: ignore 

# Import for Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="Shopify E-commerce API",
        default_version='v1',
        description="Complete e-commerce API with products, orders, cart, and reviews",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@shopify.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_view'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_view'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]