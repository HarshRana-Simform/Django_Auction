from django.contrib import admin
from django.urls import path
from core import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/protected/', views.ProtectedView.as_view(), name='protected'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/user_detail/', views.UserDetailsView.as_view(), name='user_detail'),
    path('api/create_item/', views.CreateItemView.as_view(), name='create_item'),
]
