from django.urls import path
from . import views

urlpatterns = [
    # path('', views.admin_catalog, name='admin_catalog'),
    path('login/', views.admin_login, name='admin_login'),
    path('home/', views.admin_home, name='admin_home'),
    path('search/', views.search_google_books, name='search_google_books'),
    # path('api/log-login/', views.log_login, name='log_login'),
]

# path('api/log-login/', views.log_login, name='log_login'),