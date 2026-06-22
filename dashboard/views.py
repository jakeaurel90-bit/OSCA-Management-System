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
            middle_initial=request.POST.get('middle_initial'),
            last_name=request.POST.get('last_name'),
            suffix=request.POST.get('suffix'),
            address=request.POST.get('address'),
            birthdate=request.POST.get('birthdate'), 
            gender=request.POST.get('gender'),
            phone_number=request.POST.get('phone_number'), 
            barangay=b_obj, 
            status='ACTIVE',
            has_pension='has_pension' in request.POST,
            has_medical_assistance='has_medical_assistance' in request.POST,
            has_philhealth='has_philhealth' in request.POST,
            has_sss='has_sss' in request.POST
        )
        create_log(request.user, 'CREATE', f"Registered: {senior.first_name} {senior.last_name}")
        return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/registration.html')

@login_required(login_url='dashboard:login')
def edit_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    if request.method == 'POST':
        senior.first_name = request.POST.get('first_name')
        senior.middle_initial = request.POST.get('middle_initial')
        senior.last_name = request.POST.get('last_name')
        senior.suffix = request.POST.get('suffix')
        senior.address = request.POST.get('address')
        senior.save()
        create_log(request.user, 'UPDATE', f"Edited: {senior.first_name} {senior.last_name}")
        return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/edit_senior.html', {'senior': senior})

@login_required(login_url='dashboard:login')
def delete_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    senior.is_deleted = True
    senior.save()
    create_log(request.user, 'DELETE', f"Deleted: {senior.last_name}")
    return redirect('dashboard:list_seniors')

@login_required(login_url='dashboard:login')
def restore_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    senior.is_deleted = False
    senior.save()
    return redirect('dashboard:settings')

@login_required(login_url='dashboard:login')
def mark_id_processed(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    senior.id_status = 'PROCESSED'
    senior.save()
    return redirect('dashboard:id_management')

# --- ID & OTHER MANAGEMENT ---
@login_required(login_url='dashboard:login')
def list_seniors(request): 
    return render(request, 'dashboard/list_seniors.html', {'seniors': SeniorCitizen.objects.filter(is_deleted=False)})

@login_required(login_url='dashboard:login')
def id_management_view(request): 
    return render(request, 'dashboard/id_management.html', {
        'pending_list': SeniorCitizen.objects.filter(id_status='PENDING'),
        'processed_list': SeniorCitizen.objects.filter(id_status='PROCESSED')
    })

@login_required(login_url='dashboard:login')
def benefits_view(request): 
    return render(request, 'dashboard/benefits.html', {'seniors': SeniorCitizen.objects.all()})

@login_required(login_url='dashboard:login')
def toggle_benefit(request, pk, benefit_type):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    if benefit_type == 'pension': senior.has_pension = not senior.has_pension
    elif benefit_type == 'medical': senior.has_medical_assistance = not senior.has_medical_assistance
    elif benefit_type == 'philhealth': senior.has_philhealth = not senior.has_philhealth
    elif benefit_type == 'sss': senior.has_sss = not senior.has_sss
    senior.save()
    create_log(request.user, 'UPDATE_BENEFIT', f"Toggled {benefit_type} for {senior.last_name}")
    return redirect('dashboard:benefits')

# --- REMAINING FUNCTIONS ---
def birthday_celebrants_view(request): 
    return render(request, 'dashboard/birthday_celebrants.html', {'celebrants': SeniorCitizen.objects.filter(birthdate__month=timezone.now().month)})

def reports_view(request):
    return render(request, 'dashboard/reports.html', {'barangay_stats': Barangay.objects.annotate(senior_count=Count('residents'))})

def activity_log_view(request): 
    return render(request, 'dashboard/member_logs.html', {'logs': MemberLog.objects.all().order_by('-timestamp')})

def users_view(request): 
    return render(request, 'dashboard/users.html', {'system_users': User.objects.all()})

def settings_view(request): 
    return render(request, 'dashboard/settings.html', {'deleted_seniors': SeniorCitizen.objects.filter(is_deleted=True)})