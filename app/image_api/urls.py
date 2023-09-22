from django.urls import path
from . import api_views

urlpatterns = [
    path('images/', api_views.ImageListUpload.as_view()),
    path('images/<int:pk>', api_views.ImageDetail.as_view()),
    path('images/<int:pk>/expiring_links', api_views.ExpiringLinkCreateList.as_view(), name='expiring_link_manager'),
]
