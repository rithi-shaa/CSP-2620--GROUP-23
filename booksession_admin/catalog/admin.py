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


    from django.contrib import admin

from .models import ReadingLog, ReadingGoal


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):

    list_display = (
        "log_id",
        "user",
        "book",
        "pages_read",
        "log_date",
        "created_at",
    )

    list_filter = (
        "log_date",
    )

    search_fields = (
        "user__username",
        "book__title",
    )


@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):

    list_display = (
        "goal_id",
        "user",
        "year",
        "target_numpages",
        "target_numbooks",
    )

    list_filter = (
        "year",
    )

    search_fields = (
        "user__username",
    )