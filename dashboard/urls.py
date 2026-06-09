from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'dashboard'

urlpatterns = [
    # System
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Senior Management (CRUD)
    path('seniors/', views.list_seniors, name='list_seniors'),
    path('add/', views.add_senior, name='add_senior'),
    path('edit/<int:pk>/', views.edit_senior, name='edit_senior'),
    path('delete/<int:pk>/', views.delete_senior, name='delete_senior'),
    path('settings/restore/<int:pk>/', views.restore_senior, name='restore_senior'),
    
    # ID Management
    path('id-management/', views.id_management_view, name='id_management'),
    path('id/process/<int:pk>/', views.mark_id_processed, name='mark_id_processed'),
    
    # Reports & Analytics
    path('reports/', views.reports_view, name='reports'),
    
    # Other Modules
    path('benefits/', views.benefits_view, name='benefits'),
    path('birthdays/', views.birthday_celebrants_view, name='birthday_celebrants'),
    path('logs/', views.activity_log_view, name='activity_log'),
    path('users/', views.users_view, name='users'),
    path('settings/', views.settings_view, name='settings'),
]