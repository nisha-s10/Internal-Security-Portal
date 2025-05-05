from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from employee.models import *
from datetime import datetime, timedelta
from django.views.decorators.cache import cache_control
from django.utils import timezone
from utils.decorators import employee_session_required  # ✅ Import the decorator


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@employee_session_required
def index(request):
    e_id = request.session['employee_id']
    employee = Employee.objects.get(employee_id=e_id)
    context = {'employee': employee}
    return render(request, 'employee/index.html', context)


def logout(request):
    request.session.flush()
    request.session['m'] = 'Logged out successfully.'
    return redirect('/')


def mark_attendance(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    if request.method == 'POST':
        password = request.POST.get('password')

        if password == employee.password:
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
