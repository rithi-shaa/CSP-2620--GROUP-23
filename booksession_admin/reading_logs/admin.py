from django.contrib import admin

from .models import Book, ReadingLog


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'book_id',
        'title',
    )