# accounts/urls.py
from django.urls import path
from .views import login_view, create_user, get_users, delete_user

urlpatterns = [
    path('login/', login_view, name='login'),
    path('users/create/', create_user, name='create_user'),
    path('users/', get_users, name='get_users'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
]