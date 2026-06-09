from django import forms
from .models import SeniorCitizen

class SeniorCitizenForm(forms.ModelForm):
    class Meta:
        model = SeniorCitizen
        fields = ['first_name', 'last_name', 'gender', 'birthdate', 'barangay', 'status']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }