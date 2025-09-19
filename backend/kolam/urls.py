# kolam/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/upload/', views.upload_kolam_image, name='upload_kolam_image'),
]