import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import UserProfile, Book, Shelf, ShelfBook, UserLoginLog

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
        return redirect('profile')

    return render(request, 'profile.html', {'user': request.user, 'profile': profile_obj})

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
            return render(request, 'catalog/login.html', {'error': 'Invalid credentials or not an admin.'})
            
    return render(request, 'catalog/login.html')

def admin_home(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('admin_login')

    login_logs = UserLoginLog.objects.select_related('user').order_by('-login_time')[:15]
    total_books = Book.objects.count()
    total_users = UserProfile.objects.count()

    context = {
        'login_logs': login_logs,
        'total_books': total_books,
        'total_users': total_users,
    }

    return render(request, 'catalog/admin_home.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            UserLoginLog.objects.create(user=user)
            
            messages.success(request, "Logged in successfully!")
            return redirect('shelves')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'catalog/login.html')

def index(request):
    books = Book.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'index.html', {'books': books})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def shelves(request):
    if not request.user.is_authenticated:
        return redirect('login')

    my_shelves = Shelf.objects.filter(user=request.user)
    shelves_with_books = []

    for shelf in my_shelves:
        shelf_books = ShelfBook.objects.filter(shelf=shelf).select_related('book')
        books = [{'book': sb.book, 'reading_status': sb.reading_status} for sb in shelf_books]
        shelves_with_books.append({
            'shelf_id': shelf.shelf_id,
            'shelf_name': shelf.shelf_name,
            'books': books
        })

    return render(request, 'shelves.html', {'shelves': shelves_with_books, 'username': request.user.username})

#search function
@login_required
def admin_home(request):
    logs = UserLoginLog.objects.all().order_by('-login_time')
    return render(request, 'catalog/home.html', {'logs': logs})


def search_google_books(request):
    query = request.GET.get('q', '')
    books = None
    
    if query:
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            # Fallback if no books found
            if 'items' not in data or not data['items']:
                return redirect('manual_book_entry')
                
            books = data['items']
        except requests.exceptions.RequestException:
            # Fallback if API fails
            return redirect('manual_book_entry')

    return render(request, 'catalog/search.html', {'books': books, 'query': query})

def save_book_from_api(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        published_date = request.POST.get('published_date')
        
        # Save directly to Django database model
        Book.objects.create(
            title=title,
            author=authors,
            published_date=published_date if published_date else None
        )
        return redirect('admin_home')
        
    return redirect('search_google_books')

def manual_book_entry(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        published_date = request.POST.get('published_date')
        
        Book.objects.create(
            title=title,
            author=authors,
            published_date=published_date if published_date else None
        )
        return redirect('admin_home')
        
    return render(request, 'catalog/manual_entry.html')