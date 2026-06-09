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
        'id_type', 
        'id_status',
        'is_deleted'  # Added to track soft-deleted records
    )
    list_filter = (
        'status', 
        'gender', 
        'barangay', 
        'id_type', 
        'id_status',
        'is_deleted'  # Added to filter by deletion status
    )
    search_fields = ('last_name', 'first_name', 'id_number')
    
    # Keeping id_processed_date as read-only for data integrity
    readonly_fields = ('id_processed_date',)

@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(MemberLog)
class MemberLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp',)