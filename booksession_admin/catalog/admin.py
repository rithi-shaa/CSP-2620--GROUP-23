from django.contrib import admin
from .models import Book, ReadingLog


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'book_id',
        'title',
        'genre',
        'added_by',
        'created_at',
    )
    list_filter = ('genre',)

    def save_model(self, request, obj, form, change):
        if not obj.added_by_id:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


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