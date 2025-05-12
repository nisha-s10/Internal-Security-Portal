from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from owner.models import Owner
from employee.models import Employee, Attendance
from django.views.decorators.cache import cache_control
from django.urls import reverse
from django.utils import timezone
from utils.decorators import owner_session_required  # ✅ Import your decorator
import os

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def index(request):
    o_id = request.session['owner_id']
    m = request.session.pop('m', '')
    owner = Owner.objects.get(owner_id=o_id)
    context = {'owner': owner, 'm':m}
    return render(request, 'owner/index.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def editown(request):
    o_id = request.session['owner_id']
    owner = get_object_or_404(Owner, owner_id=o_id)

    if request.method == "POST":
        old_password = owner.password
        owner.name = request.POST.get('o_name', '').strip()
        owner.gender = request.POST.get('o_gender', '').strip()
        owner.designation = request.POST.get('o_desig', '').strip()
        owner.email = request.POST.get('o_email', '').strip()
        owner.password = request.POST.get('o_pass', '')
        owner.dob = request.POST.get('o_dob', '')
        owner.aadhar_number = request.POST.get('o_adh', '').strip()
        owner.mobile_number = request.POST.get('o_mob', '').strip()

        new_photo = request.FILES.get('o_photo')
        if new_photo:
            # Delete old photo if exists
            if owner.photo and os.path.isfile(owner.photo.path):
                os.remove(owner.photo.path)
            owner.photo = new_photo

        owner.save()

        if old_password != owner.password:
            request.session.flush()  # Log out
            return render(request, 'login.html', {'m': 'Password updated successfully. Please re-login now.'})

        request.session['m'] = 'Your profile updated successfully.'
        return redirect('index')

    return render(request, 'owner/editown.html', {'owner': owner})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def empdetails(request):
    employees = Employee.objects.all()
    m = request.GET.get('m')  # 👈 fetch message
    return render(request, 'owner/empdetails.html', {'employees': employees, 'm': m})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def regemp(request):
    if request.method == "POST":
        name = request.POST.get('e_name', '').strip()
        gender = request.POST.get('e_gender')
        designation = request.POST.get('e_desig')
        email = request.POST.get('e_email', '').strip()
        password = request.POST.get('e_pass', '')
        confirm_password = request.POST.get('e_cpass', '')
        dob = request.POST.get('e_dob', '')
        mobile = request.POST.get('e_mob', '').strip()
        aadhar = request.POST.get('e_adh', '').strip()
        photo = request.FILES.get('e_photo')
        lat = request.POST.get('location_lat', '')
        lon = request.POST.get('location_lon', '')

        if not all([name, gender, designation, email, password, confirm_password, dob, mobile, aadhar, lat, lon]):
            return render(request, 'owner/regemp.html', {'m': 'All fields are required.'})
        
        if not photo:
            photo = None

        Employee.objects.create(
            name=name,
            gender=gender,
            designation=designation,
            email=email,
            password=password,  # Note: Use password hashing in production!
            dob=dob,
            aadhar_number=aadhar,
            mobile_number=mobile,
            photo=photo,
            location_lat=float(lat),
            location_lon=float(lon)
        )
        return redirect(f"{reverse('empdetails')}?m=Thank you for registration.")
    return render(request, 'owner/regemp.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def viewemp(request, id):
    try:
        emp = Employee.objects.get(pk=id)
        return render(request, 'owner/viewemp.html', {'employee': emp})
    except Employee.DoesNotExist:
        return redirect('empdetails')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def editemp(request, id):
    employee = get_object_or_404(Employee, pk=id)

    if request.method == "POST":
        employee.name = request.POST.get('e_name', '').strip()
        employee.gender = request.POST.get('e_gender', '').strip()
        employee.designation = request.POST.get('e_desig', '').strip()
        employee.email = request.POST.get('e_email', '').strip()
        employee.password = request.POST.get('e_pass', '')
        employee.dob = request.POST.get('e_dob', '')
        employee.aadhar_number = request.POST.get('e_adh', '').strip()
        employee.mobile_number = request.POST.get('e_mob', '').strip()

        new_photo = request.FILES.get('e_photo')
        if new_photo:
            # Delete old photo if exists
            if employee.photo and os.path.isfile(employee.photo.path):
                os.remove(employee.photo.path)
            employee.photo = new_photo

        try:
            employee.location_lat = float(request.POST.get('location_lat', ''))
            employee.location_lon = float(request.POST.get('location_lon', ''))
        except ValueError:
            employee.location_lat = None
            employee.location_lon = None
        
        employee.save()
        return redirect(f"{reverse('empdetails')}?m=Employee updated successfully.")

    return render(request, 'owner/editemp.html', {'employee': employee})   

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def deleteemp(request, id):
    if request.method == "POST":
        try:
            Employee.objects.get(pk=id).delete()
        except Employee.DoesNotExist:
            pass
    return redirect('empdetails')

def logout(request):
    request.session.flush()
    request.session['m'] = 'Logged out successfully.'
    return redirect('/')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def attendance_report(request):
    selected_date = request.GET.get('date')
    attendances = []

    if selected_date:
        try:
            parsed_date = datetime.strptime(selected_date, "%B %d, %Y").date()
            attendances = Attendance.objects.select_related('employee').filter(date=parsed_date).order_by('employee__name')

            for att in attendances:
                if att.entry_time and att.exit_time:
                    entry_dt = datetime.combine(att.date, att.entry_time)
                    exit_dt = datetime.combine(att.date, att.exit_time)
                    duration = exit_dt - entry_dt
                    total_seconds = int(duration.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    att.working_time = f"{hours} hr {minutes} min {seconds} sec"
                else:
                    att.working_time = None
        except ValueError:
            selected_date = None

    all_dates = Attendance.objects.values_list('date', flat=True).distinct().order_by('-date')
    formatted_dates = [d.strftime("%B %d, %Y") for d in all_dates]

    context = {
        'attendances': attendances,
        'dates': formatted_dates,
        'selected_date': selected_date,
    }
    return render(request, 'owner/attrepo.html', context)
