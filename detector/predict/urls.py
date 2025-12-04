# predict/urls.py
from django.urls import path
from . import views

app_name = "predict"

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict_image, name='predict_image'),
]