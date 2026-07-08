from django import forms
from .models import SeniorCitizen

class SeniorCitizenForm(forms.ModelForm):
    class Meta:
        model = SeniorCitizen
        fields = [
            'first_name', 'middle_initial', 'last_name', 'suffix', 
            'address', 'gender', 'civil_status', 'birthdate', 
            'age', 'phone_number', 'barangay', 'status', 
            'date_registered', 'is_deleted', 'id_status', 'id_type',
            'has_pension', 'has_sss', 'has_philhealth', 
            'has_medical_assistance'
        ]
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_registered': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_deleted': forms.HiddenInput(),
            # Apply Bootstrap styling to inputs
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'civil_status': forms.Select(attrs={'class': 'form-select'}),
            'barangay': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'id_status': forms.Select(attrs={'class': 'form-select'}),
            'id_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(SeniorCitizenForm, self).__init__(*args, **kwargs)
        # Optional: Set default values for hidden fields if new record
        if not self.instance.pk:
            self.fields['is_deleted'].initial = False
            self.fields['date_registered'].initial = forms.DateField().initial