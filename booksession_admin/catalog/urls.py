from django.urls import path
from . import views

urlpatterns = [
    path('api/log-login/', views.log_login, name='log_login'),
]