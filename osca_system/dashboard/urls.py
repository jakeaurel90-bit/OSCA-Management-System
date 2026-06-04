from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    # User Authentication Endpoints
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='dashboard/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset_complete.html'), name='password_reset_complete'),
    
    # Dashboard Core Metrics Workspace
    path('', views.dashboard_view, name='dashboard'),
    
    # Senior Members Records Management (CRUD + CSV)
    path('seniors/', views.list_seniors, name='list_seniors'),
    path('seniors/add/', views.add_senior, name='add_senior'),
    path('seniors/edit/<int:pk>/', views.edit_senior, name='edit_senior'),
    path('seniors/delete/<int:pk>/', views.delete_senior, name='delete_senior'),
    path('seniors/export-csv/', views.export_seniors_csv, name='export_csv'),
    
    # Identification Verification Workflow
    path('id-management/', views.id_management, name='id_management'),
    path('id-management/validate/<int:pk>/', views.validate_id, name='validate_id'),
    
    # Social Benefits & Assistance Programs Matrix
    path('benefits/', views.benefits_services, name='benefits'),
    path('benefits/toggle/<int:pk>/<str:benefit_type>/', views.toggle_benefit, name='toggle_benefit'),
    
    # Operations Tracking, Regional & General Analytics
    path('reports/barangay/', views.barangay_report, name='barangay_report'),
    path('reports/general/', views.general_report, name='general_report'),
    path('logs/', views.member_logs, name='member_logs'),
    path('settings/', views.settings_view, name='settings'),
]