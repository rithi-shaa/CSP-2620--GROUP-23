import os
import requests 
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, Book, Shelf, ShelfBook, UserLoginLog, User, Review
from django.db.models import Q

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('register')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.save()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('register')

    return render(request, 'catalog/user_register.html')

def forgot_password_view(request):
    """Step 1: User enters email to request a password reset link."""
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        
        if users.exists():
            for user in users:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                reset_link = request.build_absolute_uri(
                    f"/catalog/password-reset/{uid}/{token}/"
                )
                
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link to reset your password: {reset_link}",
                    from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
                    recipient_list=[user.email],
                )
                
            messages.success(request, "Password reset instructions have been sent to your email.")
        else:
            messages.error(request, "No account found with that email address.")
            
        return redirect('reset_password')

    return render(request, 'catalog/reset_password.html', {'token': None})


def reset_password_view(request, uidb64, token):
    """Step 2: User clicks the email link, verifies the token, and enters a new password."""
    try:
        # Decode the user ID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # check if user exists and token is valid
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('reset_password_token', uidb64=uidb64, token=token)

            #save the new password securely
            user.set_password(password)
            user.save()
            
            messages.success(request, "Your password has been successfully reset. You can now login.")
            return redirect('login')

        return render(request, 'catalog/reset_password.html', {'token': token})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('reset_password')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_obj.bio = request.POST.get('bio')
        profile_obj.full_name = request.POST.get('full_name')
        
        if 'profile_picture' in request.FILES:
            profile_obj.profile_picture = request.FILES['profile_picture']
            
        profile_obj.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')

    return render(request, 'catalog/user_profile.html', {'user': request.user, 'profile': profile_obj})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            UserLoginLog.objects.create(user=user)
            
            return redirect('admin_home')
        else:
          messages.error(request, 'Invalid credentials or not an admin.')
          return render(request, 'catalog/admin_login.html')

    return render(request, 'catalog/admin_login.html')
            

def admin_home(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('admin_login')

    total_books = Book.objects.count()
    total_users = UserProfile.objects.count()

    context = {
        'total_books': total_books,
        'total_users': total_users,
    }

    return render(request, 'catalog/admin_home.html', context)

@staff_member_required(login_url='admin_login')
def admin_genre_shelves(request):
    """Admin view to see books organized into shelves by genre."""
    #get all genre available in db
    genres = Book.objects.values_list('genre', flat=True).distinct()
    
    genre_shelves = []
    for genre in genres:
        if genre: #make sure genre is not empty
            books_in_genre = Book.objects.filter(genre=genre)
            genre_shelves.append({
                'genre_name': genre,
                'books': books_in_genre
            })

    context = {
        'genre_shelves': genre_shelves,
        'username': request.user.username,
    }
    return render(request, 'catalog/admin_genre_shelves.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            UserLoginLog.objects.create(user=user)
            
            messages.success(request, "Logged in successfully!")
            return redirect('collections')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'catalog/user_login.html')

def index(request):
    books = Book.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'catalog/index.html', {'books': books})

@login_required(login_url='login')
def collections(request):
    """Displays the main collections overview page (just the blocks)."""
    my_collections = Shelf.objects.filter(user=request.user)
    
    context = {
        'collections': my_collections,
        'username': request.user.username
    }
    return render(request, 'catalog/collections.html', context)


@login_required(login_url='login')
def collection_detail(request, shelf_id):
    """Displays the books inside a specific collection when its block is clicked."""
    # Get the specific collection and make sure it belongs to the logged-in user
    collection = get_object_or_404(Shelf, shelf_id=shelf_id, user=request.user)
    
    #get all books tied to this specific collection
    shelf_books = ShelfBook.objects.filter(shelf=collection).select_related('book')
    books = [{'book': sb.book, 'reading_status': sb.reading_status} for sb in shelf_books]
    
    context = {
        'collection': collection,
        'books': books,
        'username': request.user.username
    }
    return render(request, 'catalog/collection_detail.html', context)

@login_required(login_url='login')
def add_shelf(request):
    """Handles adding a new collection/shelf for the user."""
    if request.method == 'POST':
        shelf_name = request.POST.get('shelf_name')
        if shelf_name:
            Shelf.objects.create(shelf_name=shelf_name, user=request.user)
            messages.success(request, "Collection added successfully.")
        else:
            messages.error(request, "Collection name cannot be empty.")
    return redirect('collections')

@login_required(login_url='login')
def rename_shelf(request):
    """Handles renaming an existing collection for the user."""
    if request.method == 'POST':
        shelf_id = request.POST.get('shelf_id')
        new_name = request.POST.get('new_name')
        
        # Ensure the collection belongs to the logged-in user
        collection = get_object_or_404(Shelf, shelf_id=shelf_id, user=request.user)
        if new_name:
            collection.shelf_name = new_name
            collection.save()
            messages.success(request, "Collection renamed successfully.")
        else:
            messages.error(request, "Collection name cannot be empty.")
            
    return redirect('collections')

@login_required(login_url='login')
def delete_shelf(request):
    """Handles deleting a user's collection."""
    if request.method == 'POST':
        shelf_id = request.POST.get('shelf_id')
        print("DELETE SHELF ID:", shelf_id)
        
        # ensure the collection belongs to the logged-in user
        collection = get_object_or_404(Shelf, shelf_id=shelf_id, user=request.user)
        collection.delete()
        messages.success(request, "Collection deleted successfully.")
        
    return redirect('collections')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


#search function
@login_required
def admin_home(request):
    logs = UserLoginLog.objects.all().order_by('-login_time')
    return render(request, 'catalog/admin_home.html', {'logs': logs})

def search_google_books(request):
    print("=== SEARCH VIEW HIT ===")
    query = request.GET.get('q', '')

    if query:
        request.session['last_query'] = query
    
    books = None
    
    if query:
        api_url = "https://www.googleapis.com/books/v1/volumes"
        try:
            response = requests.get(api_url, params={'q': f"inauthor:{query}", 'key': os.getenv('GOOGLE_API_KEY')})
            print("--- API STATUS:", response.status_code)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and data['items']:
                seen_titles = set()
                books = []
                for item in data['items']:
                    volume_info = item.get('volumeInfo', {})
                    title = volume_info.get('title')
                    
                    # Skip if this title has already been added
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    
                    # Extract details for display and saving
                    authors = ", ".join(volume_info.get('authors', ['Unknown Author']))
                    publisher = volume_info.get('publisher', 'N/A')
                    published_date = volume_info.get('publishedDate', 'N/A')
                    genre = ", ".join(volume_info.get('categories', ['General']))
                    thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', '')
                    
                    books.append({
                        'title': title,
                        'authors': authors,
                        'publisher': publisher,
                        'published_date': published_date,
                        'genre': genre,
                        'cover_image_url': thumbnail,
                    })
            else:
                print("--- WARNING: 'items' not found or empty in data!")
                books = []
        except Exception as e:
            print("--- API ERROR TRACEBACK:", e)
            books = []
            
    return render(request, 'catalog/search.html', {'books': books, 'query': query})

def save_book_from_api(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        published_date = request.POST.get('published_date')
        publisher = request.POST.get('publisher') 
        genre = request.POST.get('genre')   
        cover_image_url = request.POST.get('cover_image_url')  
        print("--- SAVING COVER URL:", cover_image_url)    

        # Parse the year from the date string (e.g., '2008-05-12' -> 2008)
        year_val = None
        if published_date:
            try:
                year_val = int(published_date.split('-')[0])
            except (ValueError, IndexError):
                year_val = None

        # Save directly to Django database model using 'year'
        Book.objects.create(
            title=title,
            author=authors,
            publisher=publisher,
            genre=genre,
            year=year_val,
            cover_image_url=cover_image_url
        )
        
    return redirect('book_catalog')

@login_required
def book_catalog(request):
    books = Book.objects.all()
    
    # Check if the user is an admin / staff
    if request.user.is_staff or request.user.is_superuser:
        # Admin logic or tools can go here
        user_shelves = None
    else:
        # Fetch only the regular user's shelves/collections
        user_shelves = Shelf.objects.filter(user=request.user)

    # Get search/filter parameters
    query = request.GET.get('q')
    genre = request.GET.get('genre')
    year = request.GET.get('year')

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if genre:
        books = books.filter(genre__icontains=genre)
    if year:
        books = books.filter(year=year)

    total_books = books.count()

    return render(request, 'catalog/catalog.html', {
        'books': books,
        'total_books': total_books,
        'user_shelves': user_shelves,
        'is_admin': request.user.is_staff, # Pass this flag if you need it in your HTML template
    })

def manual_book_entry(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        published_date = request.POST.get('published_date')
        
        # Parse the year safely
        year_val = None
        if published_date:
            try:
                year_val = int(published_date.split('-')[0])
            except (ValueError, IndexError):
                year_val = None
        
        # Fixed: using 'year' instead of 'published_date'
        Book.objects.create(
            title=title,
            author=authors,
            year=year_val
        )
        return redirect('book_catalog')
        
    return render(request, 'catalog/manual_entry.html')

#edit and delete functions
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.genre = request.POST.get('genre')
        book.published_date = request.POST.get('published_date')
        book.save()
        return redirect('book_catalog')
    
    return render(request, 'catalog/edit_book.html', {'book': book})

def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    print(f"--- DELETE VIEW HIT --- Method: {request.method}") # For testing purposes
    if request.method == 'POST':
        print(f"Deleting book: {book.title}") # For testing purposes
        book.delete()
    return redirect('book_catalog')

# USER FEATURE: Add Book to Collection/Shelf
@login_required
def add_to_shelf(request, book_pk):
    if request.method == 'POST':
        shelf_id = request.POST.get('shelf_id')
        book = get_object_or_404(Book, pk=book_pk)
        
        # Verify the shelf exists and belongs to the current user
        shelf = get_object_or_404(Shelf, pk=shelf_id, user=request.user)
        
        # Create the relationship using the explicit ShelfBook model
        ShelfBook.objects.get_or_create(shelf=shelf, book=book)
        
    return redirect('book_catalog')




















#Review Management
@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        if rating and review_text:
            Review.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                review_text=review_text
            )
            messages.success(request, "Your review has been added successfully.")
    return redirect('book_detail', book_id=book.book_id)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        messages.error(request, "You do not have permission to edit this review.")
        return redirect('book_detail', book_id=review.book.book_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        if rating and review_text:
            review.rating = rating
            review.review_text = review_text
            review.save()
            messages.success(request, "Your review has been updated.")
            return redirect('book_detail', book_id=review.book.book_id)
            
    return render(request, 'catalog/edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user == request.user:
        book_id = review.book.book_id
        review.delete()
        messages.success(request, "Your review has been deleted.")
    else:
        messages.error(request, "You do not have permission to delete this review.")
        return redirect('book_detail', book_id=review.book.book_id)
    return redirect('book_detail', book_id=book_id)

@login_required
def collection_detail(request, shelf_id):
    collection = get_object_or_404(Shelf, pk=shelf_id, user=request.user)
    books = collection.shelfbook_set.all()
    return render(request, 'catalog/collections_detail.html', {'collection': collection, 'books': books})