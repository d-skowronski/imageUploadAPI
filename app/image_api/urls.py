from django.urls import path
from . import api_views

urlpatterns = [
    path('images/', api_views.ImageListUpload.as_view()),
]
