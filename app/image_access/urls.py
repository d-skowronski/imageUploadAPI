from django.urls import path
from . import views

urlpatterns = [
    path('original/<str:filename>/', views.original_image_view),
]
