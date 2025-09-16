"""
URL configuration for bitrix_app_5 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from contact_export import views as contact_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', contact_views.start_index, name='start_index'),
    path('index/', contact_views.index_after, name='index_after'),
    path('export_contacts/', contact_views.export_contacts, name='export_contacts'),
    path('import_contacts/', contact_views.import_contacts, name='import_contacts'),
]
