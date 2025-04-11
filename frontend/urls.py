from django.urls import path
from frontend import views

urlpatterns = [
    path('dashboard/', views.auction_dashboard, name='auction_dashboard')
]
