from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from employee.models import *
from owner.models import *
import datetime


def index(request):
    m = request.session.pop('m', None)
    return render(request, 'index.html', {'m': m})

def login(request):
    return render(request, 'login.html')

def emplog(request):
    if request.method == 'POST':
        try:
            n = request.POST['e_email']
            p = request.POST['e_pass']
            user = Employee.objects.get(email=n, password=p)

            # Store user data in session
            request.session['employee_id'] = user.employee_id
            request.session['employee_email'] = user.email

            # Store full timestamp for accurate session timeout
            current_time = datetime.datetime.now()
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

            return redirect('./employee/')  # Redirect to employee dashboard
        except Employee.DoesNotExist:
            param = {'m': 'Invalid Credentials'}
            return render(request, 'login.html', param)

    return render(request, 'login.html')

def ownerlog(request):
    if request.method == 'POST':
        try:
            n = request.POST['o_email']
            p = request.POST['o_pass']
            user = Owner.objects.get(email=n, password=p)

            # Store user data in session
            request.session['owner_id'] = user.owner_id
            request.session['owner_email'] = user.email

            # Store full timestamp for accurate session timeout
            current_time = datetime.datetime.now()
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

            return redirect('./owner/')  # Redirect to Admin dashboard
        except Owner.DoesNotExist:
            param = {'m': 'Invalid Credentials'}
            return render(request, 'login.html', param)

    return render(request, 'login.html')


def details(request, employee_id):
    # Fetch employee details using employee_id
    employee = get_object_or_404(Employee, employee_id=employee_id)

    # Render template with employee details
    return render(request, 'details.html', {'employee': employee})
