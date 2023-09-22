from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import UploadedImageSerializer, ExpiringLinkSerializer
from .models import Image, ExpiringLink
from django.shortcuts import get_object_or_404


class UploaderExpringAccess(BasePermission):
    def has_permission(self, request, view):
        return request.user.tier.expiring_link_generation_access


class ImageListUpload(generics.ListCreateAPIView):
    serializer_class = UploadedImageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        return Image.objects.filter(uploader=self.request.user)


class ImageDetail(generics.RetrieveAPIView):
    serializer_class = UploadedImageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        return Image.objects.filter(uploader=self.request.user)


class ExpiringLinkCreateList(generics.ListCreateAPIView):
    serializer_class = ExpiringLinkSerializer
    permission_classes = [IsAuthenticated, UploaderExpringAccess]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        image_pk = self.kwargs['pk']
        expiring_links = ExpiringLink.objects.filter(
            image__pk=image_pk,
            image__uploader__pk=self.request.user.pk,
        )
        return [obj for obj in expiring_links if not obj.is_expired]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"image_pk": self.kwargs['pk']})
        return context

    def dispatch(self, request, *args, **kwargs):
        # Check if related image does exist
        get_object_or_404(Image, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
