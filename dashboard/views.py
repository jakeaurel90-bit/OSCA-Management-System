from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SeniorCitizen, Barangay, MemberLog

# --- LOGGING HELPER ---
def create_log(user, action, details):
    MemberLog.objects.create(user=user, action=action, details=details)

# --- AUTHENTICATION ---
def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard:dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            create_log(user, 'LOGIN', f"User {user.username} logged in.")
            return redirect('dashboard:dashboard')
        messages.error(request, "Invalid username or password.")
    return render(request, 'dashboard/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('dashboard:login')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        create_log(request.user, 'LOGOUT', f"User {request.user.username} logged out.")
    logout(request)
    return redirect('dashboard:login')

# --- DASHBOARD ---
@login_required(login_url='dashboard:login')
def dashboard_view(request):
    now = timezone.now()
    seniors = SeniorCitizen.objects.all()
    total = seniors.count()
    active = seniors.filter(status='ACTIVE').count()
    context = {
        'total': total,
        'active': active,
        'active_pct': (active/total * 100) if total > 0 else 0,
        'inactive': seniors.filter(status='INACTIVE').count(),
        'male': seniors.filter(gender='M').count(),
        'female': seniors.filter(gender='F').count(),
        'birthdays': seniors.filter(birthdate__month=now.month).count(),
        'newly_registered': seniors.filter(date_registered__month=now.month, date_registered__year=now.year).count(),
        'barangay_data': list(seniors.values('barangay__name').annotate(count=Count('id')).order_by('-count')),
        'today': now.strftime("%B %d, %Y")
    }
    return render(request, 'dashboard/index.html', context)

# --- CRUD OPERATIONS WITH LOGGING ---
@login_required(login_url='dashboard:login')
def add_senior(request):
    if request.method == 'POST':
        b_name = request.POST.get('barangay', '').strip()
        b_obj, _ = Barangay.objects.get_or_create(name=b_name)
        senior = SeniorCitizen.objects.create(
            first_name=request.POST.get('first_name'), 
            last_name=request.POST.get('last_name'),
            birthdate=request.POST.get('birthdate'), 
            gender=request.POST.get('gender'),
            phone_number=request.POST.get('phone_number'), 
            barangay=b_obj, 
            status='ACTIVE'
        )
        create_log(request.user, 'CREATE', f"Added senior: {senior.last_name}, {senior.first_name}")
        return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/registration.html')

@login_required(login_url='dashboard:login')
def edit_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    if request.method == 'POST':
        senior.first_name = request.POST.get('first_name', senior.first_name)
        senior.last_name = request.POST.get('last_name', senior.last_name)
        senior.save()
        create_log(request.user, 'UPDATE', f"Updated senior: {senior.last_name}")
        return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/edit.html', {'senior': senior})

@login_required(login_url='dashboard:login')
def delete_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen.all_objects, pk=pk)
    if request.method == 'POST':
        senior.is_deleted = True 
        senior.save()
        create_log(request.user, 'DELETE', f"Deleted senior: {senior.last_name}")
        return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/confirm_delete.html', {'senior': senior})

@login_required(login_url='dashboard:login')
def restore_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen.all_objects, pk=pk, is_deleted=True)
    if request.method == 'POST':
        senior.is_deleted = False
        senior.save()
        create_log(request.user, 'RESTORE', f"Restored senior: {senior.last_name}")
    return redirect('dashboard:settings')

# --- ID & OTHER MANAGEMENT ---
@login_required(login_url='dashboard:login')
def mark_id_processed(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    if request.method == 'POST':
        senior.id_status = 'PROCESSED'
        senior.save()
        create_log(request.user, 'ID_PROCESS', f"Processed ID for: {senior.last_name}")
    return redirect('dashboard:id_management')

@login_required(login_url='dashboard:login')
def list_seniors(request): return render(request, 'dashboard/list_seniors.html', {'seniors': SeniorCitizen.objects.all()})

@login_required(login_url='dashboard:login')
def id_management_view(request): 
    return render(request, 'dashboard/id_management.html', {
        'pending_list': SeniorCitizen.objects.filter(id_status='PENDING'),
        'processed_list': SeniorCitizen.objects.filter(id_status='PROCESSED')
    })

@login_required(login_url='dashboard:login')
def benefits_view(request): return render(request, 'dashboard/benefits.html')

@login_required(login_url='dashboard:login')
def birthday_celebrants_view(request): 
    return render(request, 'dashboard/birthday_celebrants.html', {'celebrants': SeniorCitizen.objects.filter(birthdate__month=timezone.now().month)})

@login_required(login_url='dashboard:login')
def reports_view(request):
    return render(request, 'dashboard/reports.html', {'barangay_stats': Barangay.objects.annotate(senior_count=Count('residents'))})

@login_required(login_url='dashboard:login')
def activity_log_view(request): return render(request, 'dashboard/member_logs.html', {'logs': MemberLog.objects.all().order_by('-timestamp')})

@login_required(login_url='dashboard:login')
def users_view(request): return render(request, 'dashboard/users.html', {'system_users': User.objects.all()})

@login_required(login_url='dashboard:login')
def settings_view(request): 
    return render(request, 'dashboard/settings.html', {'deleted_seniors': SeniorCitizen.all_objects.filter(is_deleted=True)})