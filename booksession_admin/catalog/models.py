from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    story = models.TextField(blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserLoginLog(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.login_time}"