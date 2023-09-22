from django.shortcuts import HttpResponse, get_object_or_404
from django.http import HttpResponseForbidden
from image_api.models import Image, ResizedImage
from mimetypes import guess_type


def resized_image_view(request, filename):
def original_image_view(request, filename):
    slug = filename.split('.')[0]
    image = Image.objects.select_related('uploader__tier').get(slug=slug)
    if image.uploader.tier.original_link_access:
        return HttpResponse(image.file.read(), content_type=guess_type(image.file.name)[0])
    else:
        return HttpResponseForbidden()
