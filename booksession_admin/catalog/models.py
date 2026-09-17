from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

class UserLoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.login_time}"

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

class Shelf(models.Model):
    shelf_id = models.AutoField(primary_key=True)
    shelf_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class ShelfBook(models.Model):
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reading_status = models.CharField(max_length=50, default='Want to Read')

    def __str__(self):
        return f"{self.book.title} on {self.shelf.shelf_name}"
