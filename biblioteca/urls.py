from django.contrib import admin
from django.urls import path, include
from biblioteca import views
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

biblioteca_router = SimpleRouter()
# livros-list -> GET
# livros-detail -> GET, POST, PUT, DELETE
biblioteca_router.register('api/livros', views.LivroViewSet, basename='api-livros')
biblioteca_router.register('api/categorias', views.CategoriaViewSet, basename='api-livros-categoria')

urlpatterns = [
    path('', include(biblioteca_router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
