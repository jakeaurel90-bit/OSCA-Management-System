from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import SeniorCitizen, Barangay, MemberLog

# --- Helper ---
def create_log(user, action, details):
    MemberLog.objects.create(user=user, action=action, details=details)

def is_staff(user):
    return user.is_staff

# --- Auth ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
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

# --- Admin/User Management ---
@login_required(login_url='dashboard:login')
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:dashboard')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'dashboard/edit_profile.html', {'form': form})

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:dashboard')
def users_view(request): 
    return render(request, 'dashboard/users.html', {'system_users': User.objects.all()})

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:dashboard')
def add_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        is_admin = request.POST.get('is_admin') == 'on'
        if form.is_valid():
            user = form.save(commit=False)
            if is_admin:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            messages.success(request, 'New user account created successfully!')
            return redirect('dashboard:users')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/add_user.html', {'form': form})

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:dashboard')
def edit_user(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user_to_edit.username} updated successfully.")
            return redirect('dashboard:users')
    else:
        form = UserChangeForm(instance=user_to_edit)
    return render(request, 'dashboard/edit_user.html', {'form': form, 'user_to_edit': user_to_edit})

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:dashboard')
def delete_user(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
    else:
        user_to_delete.delete()
        messages.success(request, f"User {user_to_delete.username} deleted successfully.")
    return redirect('dashboard:users')

# --- Dashboard & Management ---
@login_required(login_url='dashboard:login')
def dashboard_view(request):
    now = timezone.now()
    seniors = SeniorCitizen.objects.filter(is_deleted=False)
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

@login_required(login_url='dashboard:login')
def list_seniors(request): 
    seniors = SeniorCitizen.objects.filter(is_deleted=False).order_by('last_name', 'first_name')
    return render(request, 'dashboard/list_seniors.html', {'seniors': seniors})

@login_required(login_url='dashboard:login')
def add_senior(request):
    barangays = Barangay.objects.exclude(name__icontains="txtSQL").order_by('name')
    if request.method == 'POST':
        b_id = request.POST.get('barangay')
        if b_id:
            barangay_obj = get_object_or_404(Barangay, id=b_id)
            senior = SeniorCitizen.objects.create(
                first_name=request.POST.get('first_name'),
                middle_initial=request.POST.get('middle_initial'),
                last_name=request.POST.get('last_name'),
                suffix=request.POST.get('suffix'),
                address=request.POST.get('address'),
                civil_status=request.POST.get('civil_status'),
                birthdate=request.POST.get('birthdate'),
                age=request.POST.get('age'),
                gender=request.POST.get('gender'),
                date_registered=request.POST.get('date_registered'),
                phone_number=request.POST.get('phone_number'), 
                barangay=barangay_obj, 
                status='ACTIVE',
                has_pension='has_pension' in request.POST,
                has_medical_assistance='has_medical_assistance' in request.POST,
                has_philhealth='has_philhealth' in request.POST,
                has_sss='has_sss' in request.POST
            )
            create_log(request.user, 'CREATE', f"Registered: {senior.first_name} {senior.last_name}")
            return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/registration.html', {'barangays': barangays, 'now': date.today()})

@login_required(login_url='dashboard:login')
def edit_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    barangays = Barangay.objects.exclude(name__icontains="txtSQL").order_by('name')
    if request.method == 'POST':
        b_id = request.POST.get('barangay')
        barangay_obj = get_object_or_404(Barangay, id=b_id)
        senior.first_name = request.POST.get('first_name')
        senior.middle_initial = request.POST.get('middle_initial')
        senior.last_name = request.POST.get('last_name')
        senior.suffix = request.POST.get('suffix')
        senior.address = request.POST.get('address')
        senior.civil_status = request.POST.get('civil_status')
        senior.birthdate = request.POST.get('birthdate')
        senior.age = request.POST.get('age')
        senior.gender = request.POST.get('gender')
        senior.date_registered = request.POST.get('date_registered')
        senior.phone_number = request.POST.get('phone_number')
        senior.barangay = barangay_obj
        senior.status = request.POST.get('status')
        senior.has_pension = 'has_pension' in request.POST
        senior.has_medical_assistance = 'has_medical_assistance' in request.POST
        senior.has_philhealth = 'has_philhealth' in request.POST
        senior.has_sss = 'has_sss' in request.POST
        senior.save()
        create_log(request.user, 'UPDATE', f"Edited: {senior.first_name} {senior.last_name}")
        return redirect('dashboard:list_seniors')
    return render(request, 'dashboard/edit_senior.html', {'senior': senior, 'barangays': barangays})

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
def id_management_view(request): 
    return render(request, 'dashboard/id_management.html', {
        'pending_list': SeniorCitizen.objects.filter(id_status='PENDING', is_deleted=False),
        'processed_list': SeniorCitizen.objects.filter(id_status='PROCESSED', is_deleted=False)
    })

@login_required(login_url='dashboard:login')
def mark_id_processed(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    senior.id_status = 'PROCESSED'
    senior.save()
    return redirect('dashboard:id_management')

@login_required(login_url='dashboard:login')
def benefits_view(request): 
    return render(request, 'dashboard/benefits.html', {'seniors': SeniorCitizen.objects.filter(is_deleted=False)})

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

@login_required(login_url='dashboard:login')
def birthday_celebrants_view(request): 
    return render(request, 'dashboard/birthday_celebrants.html', {'celebrants': SeniorCitizen.objects.filter(birthdate__month=timezone.now().month, is_deleted=False)})

@login_required(login_url='dashboard:login')
def activity_log_view(request): 
    return render(request, 'dashboard/member_logs.html', {'logs': MemberLog.objects.all().order_by('-timestamp')})

@login_required(login_url='dashboard:login')
def settings_view(request): 
    return render(request, 'dashboard/settings.html', {'deleted_seniors': SeniorCitizen.objects.filter(is_deleted=True)})

@login_required(login_url='dashboard:login')
def reports_view(request):
    all_seniors = SeniorCitizen.objects.filter(is_deleted=False)
    context = {
        'total_seniors': all_seniors.count(),
        'active_seniors': all_seniors.filter(status='ACTIVE').count(),
        'inactive_seniors': all_seniors.filter(status='INACTIVE').count(),
        'deceased_seniors': all_seniors.filter(status='DECEASED').count(),
        'active_beneficiaries': all_seniors.filter(
            status='ACTIVE'
        ).filter(Q(has_pension=True) | Q(has_medical_assistance=True) | Q(has_philhealth=True) | Q(has_sss=True)).count(),
        'barangay_stats': Barangay.objects.exclude(name__icontains="txtSQL").annotate(
            senior_count=Count('residents', filter=Q(residents__is_deleted=False))
        ),
        'birthday_celebrants': all_seniors.filter(birthdate__month=date.today().month).order_by('birthdate__day')
    }
    return render(request, 'dashboard/reports.html', context)