from django.http import HttpResponse
from django.shortcuts import render, redirect
import datetime
from owner.models import *
from employee.models import *
from django.views.decorators.cache import cache_control
from django.urls import reverse

# Define session timeout duration (in minutes)
ALLOTTED_TIME = 30

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if 'owner_id' in request.session:
        current_time = datetime.datetime.now()

        # Ensure 'login_time' is set in session
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Convert session login time to datetime object
        login_time = datetime.datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")

        # Check if the session has expired
        if current_time - login_time < datetime.timedelta(minutes=ALLOTTED_TIME):
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
        current_time = datetime.datetime.now()
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        login_time = datetime.datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        
        if current_time - login_time < datetime.timedelta(minutes=ALLOTTED_TIME):
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
        current_time = datetime.datetime.now()
        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        login_time = datetime.datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        
        if current_time - login_time < datetime.timedelta(minutes=ALLOTTED_TIME):
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if request.method=="POST":
                name = request.POST.get('e_name', '').strip()
                email = request.POST.get('e_email', '').strip()
                password = request.POST.get('e_pass', '')
                confirm_password = request.POST.get('e_cpass', '')
                dob = request.POST.get('e_dob', '')
                mobile = request.POST.get('e_mob', '').strip()
                aadhar = request.POST.get('e_adh', '').strip()
                photo = request.FILES.get('e_photo')

                if not all([name, email, password, confirm_password, dob, mobile, aadhar, photo]):
                    param = {'m': 'All fields are required.'}
                    return render(request, 'owner/regemp.html', param)
                
                Employee.objects.create(
                    email=email,
                    password=password,  # In production, hash this!
                    name=name,
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