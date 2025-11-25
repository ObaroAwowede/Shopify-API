from django.contrib import admin #type: ignore
from django.urls import path, include #type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # type: ignore 

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('store.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_view'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_view'),
]
