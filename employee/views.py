from django.http import HttpResponse
from django.shortcuts import render, redirect
from employee.models import *
from datetime import datetime, timedelta
from django.views.decorators.cache import cache_control
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

# Define session timeout duration (in minutes)
ALLOTTED_TIME = 2

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if 'employee_id' in request.session:
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
            e_id = request.session['employee_id']
            employee = Employee.objects.get(employee_id=e_id)
            # Pass the employee details to the template

            context = {'employee': employee}
            return render(request, 'employee/index.html', context)
        else:
            request.session.flush()  # Clear session if timeout occurs
            param = {'m': 'Session timed out. Please log in again.'}
            return render(request, 'login.html', param)
    else:
        param = {'m': 'Please log in first.'}
        return render(request, 'login.html', param)
    

def logout(request):
    request.session.flush()  # Clear session data
    request.session['m'] = 'Logged out successfully.'
    return redirect('/')




def mark_attendance(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    if request.method == 'POST':
        password = request.POST.get('password')

        if password == employee.password:  # Replace with hashed password check if needed
            today = timezone.localtime(timezone.now()).date()
            now = timezone.localtime(timezone.now()).time()

            attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

            if created:
                attendance.entry_time = now
                attendance.save()
                return render(request, 'employee/attpass.html', {
                    'employee': employee,
                    'success': f"Entry time logged for {employee.name} at {now.strftime('%H:%M:%S')}."
                })

            elif attendance.exit_time is None:
                attendance.exit_time = now
                attendance.save()
                return render(request, 'employee/attpass.html', {
                    'employee': employee,
                    'success': f"Exit time logged for {employee.name} at {now.strftime('%H:%M:%S')}."
                })

            else:
                return render(request, 'employee/attpass.html', {
                    'employee': employee,
                    'error': "Attendance already marked for today (Entry and Exit)."
                })
        else:
            return render(request, 'employee/attpass.html', {
                'employee': employee,
                'error': "Incorrect password."
            })

    return render(request, 'employee/attpass.html', {'employee': employee})
