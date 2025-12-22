from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('editown/', views.editown, name='editown'),
    path('empdetails/',views.empdetails, name='empdetails'),
    path('regemp/', views.regemp, name='regemp'),
    path('viewemp/<str:empid>/', views.viewemp, name='viewemp'),
    path('editemp/<str:empid>/', views.editemp, name='editemp'),
    path('deleteemp/<str:empid>/', views.deleteemp, name='deleteemp'),
    path('attendance-report/', views.attendance_report, name='attendance-report'),
    path('logout', views.logout, name='logout')
]