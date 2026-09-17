import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserLoginLog, Book

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_home')
        else:
            return render(request, 'catalog/login.html', {'error': 'Invalid credentials or not an admin.'})
    return render(request, 'catalog/login.html')

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