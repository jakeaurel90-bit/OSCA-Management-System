import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SeniorCitizen, Barangay, MemberLog

# ================= USER AUTHENTICATION GATEWAY =================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
        
    if request.method == 'POST':
        username_val = request.POST.get('username')
        password_val = request.POST.get('password')
        user = authenticate(request, username=username_val, password=password_val)
        
        if user is not None:
            login(request, user)
            MemberLog.objects.create(user=user, action='LOGIN', details=f"User session initialized for administrative operator: {user.username}")
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Access Denied: Invalid administrative credentials.")
            
    return render(request, 'dashboard/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        MemberLog.objects.create(user=request.user, action='LOGOUT', details=f"User session terminated for operator: {request.user.username}")
        logout(request)
    return redirect('dashboard:login')


# ================= PROTECTED ADMINISTRATIVE PANELS =================

@login_required(login_url='dashboard:login')
def dashboard_view(request):
    total_seniors = SeniorCitizen.objects.count()
    now = timezone.now()
    
    context = {
        'total_seniors': total_seniors,
        'active_count': SeniorCitizen.objects.filter(status='ACTIVE').count(),
        'inactive_count': SeniorCitizen.objects.filter(status='INACTIVE').count(),
        'birthday_count': SeniorCitizen.objects.filter(birthdate__month=now.month).count(),
    }
    return render(request, 'dashboard/index.html', context)

@login_required(login_url='dashboard:login')
def list_seniors(request):
    query = request.GET.get('search', '')
    if query:
        seniors = SeniorCitizen.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(id_number__icontains=query)
        )
    else:
        seniors = SeniorCitizen.objects.all()
    return render(request, 'dashboard/list_seniors.html', {'seniors': seniors, 'search_query': query})

@login_required(login_url='dashboard:login')
def add_senior(request):
    if request.method == 'POST':
        barangay_name = request.POST.get('barangay', '').strip()
        barangay_obj, _ = Barangay.objects.get_or_create(name=barangay_name)
        
        senior = SeniorCitizen.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            gender=request.POST.get('gender'),
            birthdate=request.POST.get('birthdate'),
            barangay=barangay_obj,
            status=request.POST.get('status', 'ACTIVE')
        )
        MemberLog.objects.create(user=request.user, action='ADD', details=f"Created database entry for senior member: {senior.last_name}, {senior.first_name}")
        return redirect('dashboard:list_seniors')
        
    return render(request, 'dashboard/registration.html')

@login_required(login_url='dashboard:login')
def edit_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    if request.method == 'POST':
        barangay_name = request.POST.get('barangay', '').strip()
        barangay_obj, _ = Barangay.objects.get_or_create(name=barangay_name)
        
        senior.first_name = request.POST.get('first_name')
        senior.last_name = request.POST.get('last_name')
        senior.gender = request.POST.get('gender')
        senior.birthdate = request.POST.get('birthdate')
        senior.barangay = barangay_obj
        senior.status = request.POST.get('status')
        senior.save()
        
        MemberLog.objects.create(user=request.user, action='EDIT', details=f"Modified registration profile records for citizen ID: {senior.id}")
        return redirect('dashboard:list_seniors')
        
    return render(request, 'dashboard/edit.html', {'senior': senior})

@login_required(login_url='dashboard:login')
def delete_senior(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    log_details = f"Permanently purged member data profile for: {senior.last_name}, {senior.first_name}"
    senior.delete()
    MemberLog.objects.create(user=request.user, action='DELETE', details=log_details)
    return redirect('dashboard:list_seniors')

@login_required(login_url='dashboard:login')
def export_seniors_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="OSCA_Masterlist_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['OSCA ID Number', 'First Name', 'Last Name', 'Gender', 'Birthdate', 'Barangay Location Area', 'Status'])
    
    for citizen in SeniorCitizen.objects.all():
        writer.writerow([
            citizen.id_number or 'UNASSIGNED',
            citizen.first_name,
            citizen.last_name,
            citizen.get_gender_display(),
            citizen.birthdate,
            citizen.barangay.name,
            citizen.status
        ])
    return response

@login_required(login_url='dashboard:login')
def id_management(request):
    seniors = SeniorCitizen.objects.all().order_by('id_validated')
    return render(request, 'dashboard/id_management.html', {'seniors': seniors})

@login_required(login_url='dashboard:login')
def validate_id(request, pk):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    senior.id_validated = True
    senior.id_processed_date = timezone.now()
    if not senior.id_number:
        senior.id_number = f"OSCA-{timezone.now().year}-{senior.id:04d}"
    senior.save()
    
    MemberLog.objects.create(user=request.user, action='ID_VERIFY', details=f"Generated card identifier configuration {senior.id_number} for {senior.last_name}")
    return redirect('dashboard:id_management')

@login_required(login_url='dashboard:login')
def benefits_services(request):
    seniors = SeniorCitizen.objects.filter(status='ACTIVE')
    return render(request, 'dashboard/benefits.html', {'seniors': seniors})

@login_required(login_url='dashboard:toggle_benefit')
def toggle_benefit(request, pk, benefit_type):
    senior = get_object_or_404(SeniorCitizen, pk=pk)
    if benefit_type == 'pension': senior.has_pension = not senior.has_pension
    elif benefit_type == 'sss': senior.has_sss = not senior.has_sss
    elif benefit_type == 'philhealth': senior.has_philhealth = not senior.has_philhealth
    elif benefit_type == 'medical': senior.has_medical_assistance = not senior.has_medical_assistance
    senior.save()
    
    MemberLog.objects.create(user=request.user, action='BENEFIT_UPDATE', details=f"Altered program program distribution flags for member profile: {senior.last_name}")
    return redirect('dashboard:benefits')

@login_required(login_url='dashboard:login')
def barangay_report(request):
    barangays = Barangay.objects.annotate(
        active_members=Count('residents', filter=Q(residents__status='ACTIVE')),
        inactive_members=Count('residents', filter=Q(residents__status='INACTIVE')),
        total_members=Count('residents')
    ).order_by('name')
    return render(request, 'dashboard/reports.html', {'barangays': barangays})

@login_required(login_url='dashboard:login')
def general_report(request):
    context = {
        'total_seniors': SeniorCitizen.objects.count(),
        'pension_count': SeniorCitizen.objects.filter(has_pension=True, status='ACTIVE').count(),
        'philhealth_count': SeniorCitizen.objects.filter(has_philhealth=True, status='ACTIVE').count(),
        'sss_count': SeniorCitizen.objects.filter(has_sss=True, status='ACTIVE').count(),
        'medical_aid_count': SeniorCitizen.objects.filter(has_medical_assistance=True, status='ACTIVE').count(),
    }
    return render(request, 'dashboard/general_report.html', context)

@login_required(login_url='dashboard:login')
def member_logs(request):
    logs = MemberLog.objects.all().order_by('-timestamp')
    return render(request, 'dashboard/member_logs.html', {'logs': logs})

@login_required(login_url='dashboard:login')
def settings_view(request):
    return render(request, 'dashboard/settings.html')