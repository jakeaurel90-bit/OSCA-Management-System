from django import forms
from .models import SeniorCitizen

class SeniorCitizenForm(forms.ModelForm):
    class Meta:
        model = SeniorCitizen
        fields = [
            'first_name', 'middle_initial', 'last_name', 'suffix', 
            'address', 'gender', 'civil_status', 'birthdate', 
            'age', 'phone_number', 'barangay', 'status', 
            'date_registered', 'is_deleted', 'id_status', 
            'has_pension', 'has_sss', 'has_philhealth', 
            'has_medical_assistance'
        ]
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'date_registered': forms.DateInput(attrs={'type': 'date'}),
            # Hide these fields so they are sent with the form but not shown to users
            'is_deleted': forms.HiddenInput(),
            'date_registered': forms.HiddenInput(),
        }