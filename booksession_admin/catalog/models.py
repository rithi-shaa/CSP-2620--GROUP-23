from django.conf import settings
from django.core.validators import MinValueValidator
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

class Shelf(models.Model):
    shelf_id = models.AutoField(primary_key=True)
    shelf_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shelves')

    def __str__(self):
        return self.shelf_name

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    story = models.TextField(blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return self.title

class ShelfBook(models.Model):
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reading_status = models.CharField(
        max_length=20,
        choices=[
            ('to_read', 'To Read'),
            ('reading', 'Reading'),
            ('finished', 'Finished'),
        ],
        default='to_read',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} on {self.shelf.shelf_name}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class ReadingLog(models.Model):
    log_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_logs"
    )

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="reading_logs"
    )

    pages_read = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )

    log_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-log_date", "-created_at"]

    def __str__(self):
        return f"{self.user} - {self.book} - {self.pages_read} pages"

    
class ReadingGoal(models.Model):
    goal_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_goals"
    )

    year = models.PositiveIntegerField()

    target_numpages = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    target_numbooks = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "year"],
                name="unique_reading_goal_per_user_year"
            )
        ]
        ordering = ["-year"]

    def __str__(self):
        return f"{self.user} - {self.year} Reading Goal"