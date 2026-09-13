from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserLoginLog

@csrf_exempt
def log_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        UserLoginLog.objects.create(
            username=data.get('username'),
            email=data.get('email')
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'POST only'}, status=405)