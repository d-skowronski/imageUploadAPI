from django.shortcuts import HttpResponse, get_object_or_404
from django.http import HttpResponseForbidden
from image_api.models import Image, ResizedImage
from mimetypes import guess_type


def resized_image_view(request, filename):
    slug = filename.split('.')[0]
    image = get_object_or_404(ResizedImage, slug=slug)
    return HttpResponse(image.resized_file.read(), content_type=guess_type(image.resized_file.name)[0])


def original_image_view(request, filename):
    slug = filename.split('.')[0]
    image = Image.objects.select_related('uploader__tier').get(slug=slug)
    if image.uploader.tier.original_link_access:
        return HttpResponse(image.file.read(), content_type=guess_type(image.file.name)[0])
    else:
        return HttpResponseForbidden()