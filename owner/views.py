from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta, date
from owner.models import *
from employee.models import *
from django.views.decorators.cache import cache_control
from django.urls import reverse
from django.db.models import Prefetch
from django.utils import timezone

# Define session timeout duration (in minutes)
ALLOTTED_TIME = 2

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if 'owner_id' in request.session:
        current_time = timezone.localtime(timezone.now())

        # Ensure 'login_time' is set in session
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        naive_login_time = datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        # Convert session login time to datetime object
        login_time = timezone.make_aware(naive_login_time, timezone.get_current_timezone())

        # Check if the session has expired
        if current_time - login_time < timedelta(minutes=ALLOTTED_TIME):
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")  # Update login time
            o_id = request.session['owner_id']
            owner = Owner.objects.get(owner_id=o_id)
            # Pass the owner details to the template
            context = {'owner': owner}
            return render(request, 'owner/index.html', context)
        else:
            request.session.flush()  # Clear session if timeout occurs
            param = {'m': 'Session timed out. Please log in again.'}
            return render(request, 'login.html', param)
    else:
        param = {'m': 'Please log in first.'}
        return render(request, 'login.html', param)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def empdetails(request):
    if 'owner_id' in request.session:
        current_time = timezone.localtime(timezone.now())
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        naive_login_time = datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        # Convert session login time to datetime object
        login_time = timezone.make_aware(naive_login_time, timezone.get_current_timezone())
        
        if current_time - login_time < timedelta(minutes=ALLOTTED_TIME):
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            employees = Employee.objects.all()
            m = request.GET.get('m')  # 👈 fetch message
            return render(request, 'owner/empdetails.html', {'employees': employees, 'm': m})
        else:
            request.session.flush()
            return render(request, 'login.html', {'m': 'Session timed out. Please log in again.'})
    else:
        return render(request, 'login.html', {'m': 'Please log in first.'})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def regemp(request):
    if 'owner_id' in request.session:
        current_time = timezone.localtime(timezone.now())
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        naive_login_time = datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        # Convert session login time to datetime object
        login_time = timezone.make_aware(naive_login_time, timezone.get_current_timezone())
        
        if current_time - login_time < timedelta(minutes=ALLOTTED_TIME):
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if request.method=="POST":
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
                    param = {'m': 'All fields are required.'}
                    return render(request, 'owner/regemp.html', param)
                
                Employee.objects.create(
                    email=email,
                    password=password,  # In production, hash this!
                    name=name,
                    designation=designation,
                    dob=dob,
                    aadhar_number=aadhar,
                    mobile_number=mobile,
                    photo=photo
                )
                employees = Employee.objects.all()
                param={'m':'Thank you for registration.','employees': employees}
                return redirect(f"{reverse('empdetails')}?m=Thank you for registration.")
            else:
                return render(request, 'owner/regemp.html')
        else:
            request.session.flush()
            return render(request, 'login.html', {'m': 'Session timed out. Please log in again.'})
    else:
        return render(request, 'login.html', {'m': 'Please log in first.'})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewemp(request, id):
    if 'owner_id' in request.session:
        try:
            emp = Employee.objects.get(pk=id)
            return render(request, 'owner/viewemp.html', {'employee': emp})
        except Employee.DoesNotExist:
            return redirect('empdetails')
    else:
        return redirect('login')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deleteemp(request, id):
    if 'owner_id' in request.session:
        if request.method == "POST":
            try:
                Employee.objects.get(pk=id).delete()
                return redirect('empdetails')
            except Employee.DoesNotExist:
                return redirect('empdetails')
        else:
            return redirect('empdetails')
    else:
        return redirect('login')

def logout(request):
    request.session.flush()  # Clear session data
    request.session['m'] = 'Logged out successfully.'
    return redirect('/')

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