from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import ReadingLog

@login_required
def reading_logs(request):

    logs = ReadingLog.objects.select_related('book').filter(
        user=request.user
    ).order_by('-log_date')