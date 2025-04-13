from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('empdetails/',views.empdetails, name='empdetails'),
    path('regemp/', views.regemp, name='regemp'),
    path('viewemp/<int:id>/', views.viewemp, name='viewemp'),
    path('deleteemp/<int:id>/', views.deleteemp, name='deleteemp'),
    path('logout', views.logout, name='logout')
]