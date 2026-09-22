from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class ReadingLog(models.Model):
    log_id = models.AutoField(primary_key=True)

    pages_read = models.IntegerField()

    log_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        db_column='book_id'
    )
