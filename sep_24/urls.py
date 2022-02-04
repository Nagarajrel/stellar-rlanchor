from django.urls import path
from .views import info

urlpatterns = [
    path('info', info, name='info')
]
