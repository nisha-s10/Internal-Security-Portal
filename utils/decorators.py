from functools import wraps
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect

ALLOTTED_TIME = 2  # in minutes

def owner_session_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'owner_id' not in request.session:
            return render(request, 'login.html', {'m': 'Please log in first.'})
        
        current_time = timezone.localtime(timezone.now())

        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        naive_login_time = datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        login_time = timezone.make_aware(naive_login_time, timezone.get_current_timezone())

        if current_time - login_time >= timedelta(minutes=ALLOTTED_TIME):
            request.session.flush()
            return render(request, 'login.html', {'m': 'Session timed out. Please log in again.'})

        request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")  # Refresh session
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def employee_session_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'employee_id' not in request.session:
            return render(request, 'login.html', {'m': 'Please log in first.'})
        
        current_time = timezone.localtime(timezone.now())

        if 'login_time' not in request.session:
            request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        naive_login_time = datetime.strptime(request.session['login_time'], "%Y-%m-%d %H:%M:%S")
        login_time = timezone.make_aware(naive_login_time, timezone.get_current_timezone())

        if current_time - login_time >= timedelta(minutes=ALLOTTED_TIME):
            request.session.flush()
            return render(request, 'login.html', {'m': 'Session timed out. Please log in again.'})

        request.session['login_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
