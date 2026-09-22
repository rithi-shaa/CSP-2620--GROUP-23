from django import forms

from .models import ReadingLog

class ReadingLogForm(forms.ModelForm):

    class Meta:
        model = ReadingLog

        fields = [
            'book',
            'pages_read',
            'log_date',
        ]