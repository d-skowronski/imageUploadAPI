from django.urls import path
from . import views

urlpatterns = [
    path('original/<str:filename>/', views.original_image_view),
    path('resized/<str:filename>/', views.resized_image_view),
    path('expiring/<str:pk>/', views.expiringImageView, name='expiring_link')
]
