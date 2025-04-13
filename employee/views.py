from django.http import HttpResponse
from django.shortcuts import render, redirect
from employee.models import *
import datetime
from django.views.decorators.cache import cache_control

# Define session timeout duration (in minutes)
ALLOTTED_TIME = 2

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if 'employee_id' in request.session:
        current_time = datetime.datetime.now()

        # Ensure 'login_time' is set in session
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Convert session login time to datetime object
        login_time = datetime.datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")

        # Check if the session has expired
        if current_time - login_time < datetime.timedelta(minutes=ALLOTTED_TIME):
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
