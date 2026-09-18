from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('index/', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('password-reset/', views.forgot_password_view, name='reset_password'),
    path('password-reset/<str:uidb64>/<str:token>/', views.reset_password_view, name='reset_password_token'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.admin_home, name='admin_home'),
    path('profile/', views.profile, name='profile'),
    path('shelves/', views.shelves, name='shelves'),
    # path('', views.admin_catalog, name='admin_catalog'),
    path('search/', views.search_google_books, name='search_google_books'),
    # path('api/log-login/', views.log_login, name='log_login'),
]

# path('api/log-login/', views.log_login, name='log_login'),