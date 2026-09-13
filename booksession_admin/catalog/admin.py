from django.contrib import admin
from .models import Book, UserLoginLog

admin.site.register(Book)
admin.site.register(UserLoginLog)