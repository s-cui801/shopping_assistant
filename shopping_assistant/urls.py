from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('assistant/', views.assistant_view, name='assistant'),
    path('logout/', LogoutView.as_view(), name='logout'),
]