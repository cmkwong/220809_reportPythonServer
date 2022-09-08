from django.urls import path
from . import views
from . import models

urlpatterns = [
    path('test/', views.generateComparePlotImages)
]