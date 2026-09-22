from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def reading_logs(request):
    logs = ReadingLog.objects.filter(
        user_id=request.user.id
    ).select_related('book').order_by('-log_date')

    return render(request, 'reading_logs.html', {
        'logs': logs
    })