from django.contrib import admin
from .models import Barangay, SeniorCitizen, MemberLog

@admin.register(SeniorCitizen)
class SeniorCitizenAdmin(admin.ModelAdmin):
    list_display = (
        'last_name', 
        'first_name', 
        'gender', 
        'barangay', 
        'status', 
        'is_deleted'
    )
    list_filter = (
        'status', 
        'gender', 
        'barangay', 
        'is_deleted'
    )
    search_fields = ('last_name', 'first_name', 'id_number')
    
    # Removed readonly_fields since id_processed_date no longer exists in the model

@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(MemberLog)
class MemberLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp',)