from django.contrib import admin
from .models import Image, ResizedImage, ExpiringLink

admin.site.register(Image)
admin.site.register(ResizedImage)
admin.site.register(ExpiringLink)
