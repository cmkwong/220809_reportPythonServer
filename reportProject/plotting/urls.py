from django.urls import path
from . import views
from . import models

urlpatterns = [
    path('compare', models.generateComparePlotImages_req)
]