from django import forms

from .models import (
    ReadingLog,
    ReadingGoal,
    Book,
    ShelfBook,
)


# =========================================================
# READING LOG FORM
# =========================================================

class ReadingLogForm(forms.ModelForm):

    class Meta:

        model = ReadingLog

        fields = [
            "book",
            "pages_read",
            "log_date",
        ]

        widgets = {

            "pages_read": forms.NumberInput(
                attrs={
                    "min": 0,
                    "placeholder": "Enter pages read"
                }
            ),

            "log_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # ONLY SHOW BOOKS FROM THE USER'S COLLECTION
        # -------------------------------------------------

        if user:

            book_ids = ShelfBook.objects.filter(
                shelf__user=user
            ).values_list(
                "book_id",
                flat=True
            ).distinct()

            self.fields["book"].queryset = Book.objects.filter(
                pk__in=book_ids
            ).order_by("title")

        else:

            self.fields["book"].queryset = Book.objects.none()


# =========================================================
# READING GOAL FORM
# =========================================================

class ReadingGoalForm(forms.ModelForm):

    class Meta:

        model = ReadingGoal

        fields = [
            "year",
            "target_numpages",
            "target_numbooks",
        ]

        widgets = {

            "year": forms.NumberInput(
                attrs={
                    "min": 2000
                }
            ),

            "target_numpages": forms.NumberInput(
                attrs={
                    "min": 1,
                    "placeholder": "Target pages"
                }
            ),

            "target_numbooks": forms.NumberInput(
                attrs={
                    "min": 1,
                    "placeholder": "Target books"
                }
            ),
        }

    def clean_target_numpages(self):

        value = self.cleaned_data["target_numpages"]

        if value <= 0:
            raise forms.ValidationError(
                "The annual page goal must be greater than zero."
            )

        return value

    def clean_target_numbooks(self):

        value = self.cleaned_data["target_numbooks"]

        if value <= 0:
            raise forms.ValidationError(
                "The annual book goal must be greater than zero."
            )

        return value