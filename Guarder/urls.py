"""
URL configuration for Guarder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('employee/', include('employee.urls')),
    path('emplog',views.emplog,name='emplog'),
    path('owner/', include('owner.urls')),
    path('ownerlog',views.ownerlog,name='ownerlog'),
    path('details/<str:employee_id>/', views.details, name='details'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
