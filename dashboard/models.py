from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Barangay(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

# Custom Manager to handle Soft Deletes automatically
class SeniorCitizenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SeniorCitizen(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')]
    ID_TYPE_CHOICES = [('SSS', 'SSS'), ('PHILHEALTH', 'PhilHealth'), ('GSIS', 'GSIS'), ('NONE', 'None')]
    ID_STATUS_CHOICES = [('PENDING', 'Pending'), ('PROCESSED', 'Processed')]
    
    phone_validator = RegexValidator(regex=r'^\+63[0-9]{10}$', message="Format: +639XXXXXXXXX")

    id_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthdate = models.DateField()
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='residents')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    date_registered = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, default='NONE')
    id_status = models.CharField(max_length=20, choices=ID_STATUS_CHOICES, default='PENDING')
    id_processed_date = models.DateTimeField(null=True, blank=True)
    
    has_pension = models.BooleanField(default=False)
    has_sss = models.BooleanField(default=False)
    has_philhealth = models.BooleanField(default=False)
    has_medical_assistance = models.BooleanField(default=False)

    # Use the custom manager
    objects = SeniorCitizenManager()
    # Allow access to deleted items if absolutely necessary
    all_objects = models.Manager()

    def __str__(self): return f"{self.last_name}, {self.first_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

class MemberLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)