from django.urls import path
from . import views
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

app_name = 'dashboard'

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    
    # Password Management
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='dashboard/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='dashboard/password_change_done.html'), name='password_change_done'),
    
    # Senior Management
    path('seniors/', views.list_seniors, name='list_seniors'),
    path('add/', views.add_senior, name='add_senior'),
    path('edit/<int:pk>/', views.edit_senior, name='edit_senior'),
    path('delete/<int:pk>/', views.delete_senior, name='delete_senior'),
    
    # Settings & Recycle Bin
    path('settings/', views.settings_view, name='settings'),
    path('settings/restore/<int:pk>/', views.restore_senior, name='restore_senior'),
    path('settings/delete-permanent/<int:pk>/', views.permanent_delete, name='permanent_delete'),
    path('settings/delete-all-permanent/', views.permanent_delete_all, name='permanent_delete_all'),
    
    # Other paths...
    path('id-management/', views.id_management_view, name='id_management'),
    path('id/process/<int:pk>/', views.mark_id_processed, name='mark_id_processed'),
    path('reports/', views.reports_view, name='reports'),
    path('benefits/', views.benefits_view, name='benefits'),
    path('benefits/toggle/<int:pk>/<str:benefit_type>/', views.toggle_benefit, name='toggle_benefit'),
    path('birthdays/', views.birthday_celebrants_view, name='birthday_celebrants'),
    path('logs/', views.activity_log_view, name='activity_log'),
    path('users/', views.users_view, name='users'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
]