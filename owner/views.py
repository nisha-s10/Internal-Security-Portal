from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from owner.models import Owner
from employee.models import Employee, Attendance
from django.views.decorators.cache import cache_control
from django.urls import reverse
from django.utils import timezone
from utils.decorators import owner_session_required  # ✅ Import your decorator

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@owner_session_required
def index(request):
    o_id = request.session['owner_id']
    owner = Owner.objects.get(owner_id=o_id)
    return render(request, 'owner/index.html', {'owner': owner})

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
        designation = request.POST.get('e_desig')
        email = request.POST.get('e_email', '').strip()
        password = request.POST.get('e_pass', '')
        confirm_password = request.POST.get('e_cpass', '')
        dob = request.POST.get('e_dob', '')
        mobile = request.POST.get('e_mob', '').strip()
        aadhar = request.POST.get('e_adh', '').strip()
        photo = request.FILES.get('e_photo')

        if not all([name, designation, email, password, confirm_password, dob, mobile, aadhar, photo]):
            return render(request, 'owner/regemp.html', {'m': 'All fields are required.'})

        Employee.objects.create(
            email=email,
            password=password,  # Note: Use password hashing in production!
            name=name,
            designation=designation,
            dob=dob,
            aadhar_number=aadhar,
            mobile_number=mobile,
            photo=photo
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
        employee.designation = request.POST.get('e_desig', '').strip()
        employee.email = request.POST.get('e_email', '').strip()
        employee.mobile_number = request.POST.get('e_mob', '').strip()
        employee.dob = request.POST.get('e_dob', '')
        employee.aadhar_number = request.POST.get('e_adh', '').strip()

        if request.FILES.get('e_photo'):
            employee.photo = request.FILES['e_photo']

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
