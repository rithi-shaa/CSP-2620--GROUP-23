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

    #user
    path('profile/', views.profile, name='profile'),
    path('collections/', views.shelves, name='shelves'),
    path('collection/<int:shelf_id>/', views.collection_detail, name='collection_detail'),
    path('collection/add/', views.add_shelf, name='add_shelf'),
    path('collection/rename/', views.rename_shelf, name='rename_shelf'),
    path('collection/delete/', views.delete_shelf, name='delete_shelf'),

    #admin
    path('admin/genre-shelves/', views.admin_genre_shelves, name='admin_genre_shelves'),

    
    path('search/', views.search_google_books, name='search_google_books'),
    path('manual-entry/', views.manual_book_entry, name='manual_book_entry'),
    path('save-book/', views.save_book_from_api, name='save_book_from_api'),
    path('books/', views.book_catalog, name='book_catalog'),
    # path('api/log-login/', views.log_login, name='log_login'),
]

# path('api/log-login/', views.log_login, name='log_login'),