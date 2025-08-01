from django.contrib.auth import views as auth_views
from django.urls import path

from users import views


app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path(
        'login/confirm/',
        views.LoginConfirmView.as_view(),
        name='login-confirm',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
