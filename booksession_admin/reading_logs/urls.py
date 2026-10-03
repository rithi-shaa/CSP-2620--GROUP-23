from django.urls import path
from . import views

urlpatterns = [
    path(
        'reading_logs/',
        views.reading_logs,
        name='reading_logs'
    ),
]