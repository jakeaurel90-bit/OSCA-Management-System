from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Barangay(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class SeniorCitizen(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')]
    
    id_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthdate = models.DateField()
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='residents')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    date_registered = models.DateTimeField(default=timezone.now)
    
    # ID Verification Workflow State
    id_validated = models.BooleanField(default=False)
    id_processed_date = models.DateTimeField(null=True, blank=True)

    # Benefits Program Opt-ins
    has_pension = models.BooleanField(default=False)
    has_sss = models.BooleanField(default=False)
    has_philhealth = models.BooleanField(default=False)
    has_medical_assistance = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

class MemberLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('ADD', 'Added Record'),
        ('EDIT', 'Edited Record'),
        ('DELETE', 'Deleted Record'),
        ('ID_VERIFY', 'ID Validated'),
        ('BENEFIT_UPDATE', 'Benefits Altered'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)