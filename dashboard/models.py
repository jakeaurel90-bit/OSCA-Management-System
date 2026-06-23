from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Barangay(models.Model):
    # Kidapawan City Barangays
    BARANGAY_CHOICES = [
        ('Amas', 'Amas'), ('Amazion', 'Amazion'), ('Balabag', 'Balabag'), ('Balindog', 'Balindog'),
        ('Binoligan', 'Binoligan'), ('Birada', 'Birada'), ('Gayola', 'Gayola'), ('Ginatilan', 'Ginatilan'),
        ('Ilomavis', 'Ilomavis'), ('Indangan', 'Indangan'), ('Junction', 'Junction'), ('Kalaisan', 'Kalaisan'),
        ('Kalasuyan', 'Kalasuyan'), ('Katipunan', 'Katipunan'), ('Lanao', 'Lanao'), ('Linangcob', 'Linangcob'),
        ('Luvimin', 'Luvimin'), ('Macebolig', 'Macebolig'), ('Magsaysay', 'Magsaysay'), ('Malinan', 'Malinan'),
        ('Manongol', 'Manongol'), ('Marbel', 'Marbel'), ('Mateo', 'Mateo'), ('Meohao', 'Meohao'),
        ('Mua-an', 'Mua-an'), ('New Bohol', 'New Bohol'), ('Nuangan', 'Nuangan'), ('Onica', 'Onica'),
        ('Paco', 'Paco'), ('Patadon', 'Patadon'), ('Perez', 'Perez'), ('Poblacion', 'Poblacion'),
        ('San Isidro', 'San Isidro'), ('San Roque', 'San Roque'), ('Santo Niño', 'Santo Niño'),
        ('Sibawan', 'Sibawan'), ('Sikitan', 'Sikitan'), ('Singao', 'Singao'), ('Sudapin', 'Sudapin'),
        ('Sumbao', 'Sumbao')
    ]
    name = models.CharField(max_length=50, choices=BARANGAY_CHOICES, unique=True)
    def __str__(self): return self.name

class SeniorCitizenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SeniorCitizen(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')]
    ID_STATUS_CHOICES = [('PENDING', 'Pending'), ('PROCESSED', 'Processed')]
    
    phone_validator = RegexValidator(regex=r'^\+63[0-9]{10}$', message="Format: +639XXXXXXXXX")

    # Enforcing 20-character limits as requested
    first_name = models.CharField(max_length=20)
    middle_initial = models.CharField(max_length=2, blank=True, null=True)
    last_name = models.CharField(max_length=20)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=50, default='Not specified') # Limit to 50
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthdate = models.DateField()
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='residents')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    date_registered = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    
    id_status = models.CharField(max_length=20, choices=ID_STATUS_CHOICES, default='PENDING')
    
    has_pension = models.BooleanField(default=False)
    has_sss = models.BooleanField(default=False)
    has_philhealth = models.BooleanField(default=False)
    has_medical_assistance = models.BooleanField(default=False)

    objects = SeniorCitizenManager()
    all_objects = models.Manager()

    def __str__(self): return f"{self.last_name}, {self.first_name}"

class MemberLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)