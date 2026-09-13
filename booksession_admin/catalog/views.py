from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserLoginLog

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


@login_required
def admin_home(request):
    logs = UserLoginLog.objects.all().order_by('-login_time')
    return render(request, 'catalog/home.html', {'logs': logs})