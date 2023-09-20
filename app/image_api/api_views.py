from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UploadedImageSerializer
from .models import Image


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
