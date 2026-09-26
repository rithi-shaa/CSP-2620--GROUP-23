from django import forms
from django.utils import timezone

from .models import ReadingLog, ReadingGoal


class ReadingLogForm(forms.ModelForm):

    class Meta:
        model = ReadingLog
        fields = ["book", "pages_read", "log_date"]

        widgets = {
            "book": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "pages_read": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Enter pages read"
                }
            ),

            "log_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
        }

    def clean_pages_read(self):
        pages = self.cleaned_data.get("pages_read")

        if pages is None:
            raise forms.ValidationError(
                "Please enter the number of pages read."
            )

        if pages < 0:
            raise forms.ValidationError(
                "Pages read cannot be negative."
            )

        return pages

    def clean_log_date(self):
        log_date = self.cleaned_data.get("log_date")

        if not log_date:
            raise forms.ValidationError(
                "Please enter a valid reading date."
            )

        return log_date


class ReadingGoalForm(forms.ModelForm):

    class Meta:
        model = ReadingGoal
        fields = [
            "year",
            "target_numpages",
            "target_numbooks"
        ]

        widgets = {
            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "2000"
                }
            ),

            "target_numpages": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Example: 10000"
                }
            ),

            "target_numbooks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Example: 20"
                }
            ),
        }

    def clean_target_numpages(self):
        pages = self.cleaned_data.get("target_numpages")

        if pages is None or pages <= 0:
            raise forms.ValidationError(
                "Your annual page goal must be greater than zero."
            )

        return pages

    def clean_target_numbooks(self):
        books = self.cleaned_data.get("target_numbooks")

        if books is None or books <= 0:
            raise forms.ValidationError(
                "Your annual book goal must be greater than zero."
            )

        return books