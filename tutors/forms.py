from django import forms
from .models import TutorAvailability


class TutorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TutorAvailability
        fields = ['day', 'start_time', 'end_time', 'is_active']

        widgets = {
            'day': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }