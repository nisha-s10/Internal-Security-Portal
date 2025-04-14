from django.contrib import admin
from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('logout', views.logout, name='logout')
]