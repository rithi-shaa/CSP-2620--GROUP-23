from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='user_login'),
    path('index/', views.index, name='index'),
    path('user_register/', views.user_register, name='user_register'),
    path('password_reset/', views.forgot_password_view, name='reset_password'),
    path('password_reset/<str:uidb64>/<str:token>/', views.reset_password_view, name='reset_password_token'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.admin_home, name='admin_home'),

    #user
    path('user_profile/', views.user_profile, name='user_profile'),
    path('collections/', views.collections, name='collections'),
    path('collection/<int:shelf_id>/', views.collection_detail, name='collection_detail'),
    path('collection/add/', views.add_shelf, name='add_shelf'),
    path('collection/rename/', views.rename_shelf, name='rename_shelf'),
    path('collection/delete/', views.delete_shelf, name='delete_shelf'),

    #admin
    path('admin/genre-shelves/', views.admin_genre_shelves, name='admin_genre_shelves'),
    path('admin/add-book/', views.manual_book_entry, name='add_book'),
    
    path('search/', views.search_google_books, name='search_google_books'),
    path('manual-entry/', views.manual_book_entry, name='manual_book_entry'),
    path('save-book/', views.save_book_from_api, name='save_book_from_api'),
    path('books/', views.book_catalog, name='book_catalog'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),

    # path('api/log-login/', views.log_login, name='log_login'),
]

# path('api/log-login/', views.log_login, name='log_login'),

#from django.contrib import admin
#from django.urls import path, include


#urlpatterns = [
 #   path('admin/', admin.site.urls),

    #path('', include('reading_logs.urls')),
#]