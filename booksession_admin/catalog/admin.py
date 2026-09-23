from django.contrib import admin
from .models import Book, UserProfile

admin.site.register(Book)
admin.site.register(UserProfile)

from django.contrib import admin

from .models import Book, ReadingLog


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'book_id',
        'title',
    )


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = (
        'log_id',
        'book',
        'user',
        'pages_read',
        'log_date',
        'created_at',
    )

    list_filter = (
        'log_date',
    )