from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from .utils import generate_slug_from_title
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as ImageManager
from io import BytesIO
import os
import mimetypes


class Image(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    file = models.ImageField(upload_to='original')
    title = models.CharField(max_length=255, blank=True, null=True)
    uploader = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.file.name.split('.')[0]
        if not self.slug:
            self.slug = generate_slug_from_title(self.title)
            self.file.name = f'{self.slug}.{self.file.name.split(".")[-1]}'
        self.full_clean()
        super().save(*args, **kwargs)


class ResizedImage(models.Model):
    '''Resized image with lazy generation\n
    Initialy an empty file with basic data is generated. You can use .file to access it.
    Upon first access to .resized_file an processed image will be generated and replace an empty file.
    '''
    slug = models.SlugField(unique=True)
    file = models.ImageField(upload_to='resized', null=True, blank=True)
    original = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='resizes')
    height = models.PositiveIntegerField()
    generated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug_from_title(self.original.title)
        if not self.file:
            self._generate_mock_file()
        self.full_clean()
        super().save(*args, **kwargs)

    def _generate_mock_file(self):
        '''Mock file is used to obtain basic information like name and URL'''
        self.file = ContentFile(content='', name=f'{self.slug}.{self.original.file.name.split(".")[-1]}')

    @property
    def resized_file(self):
        '''Getter around .file, makes sure resized image is generated'''
        if not self.generated:
            self.generate_resized_image()

        return self.file

    def generate_resized_image(self):
        original_image = ImageManager.open(self.original.file.path)
        original_image.thumbnail((self.height, self.height))
        with BytesIO() as temp_buffer:
            original_image.save(temp_buffer, format=original_image.format)
            newfile = InMemoryUploadedFile(
                temp_buffer,
                None,
                self.file.name,
                mimetypes.guess_type(self.file.name)[0],
                temp_buffer.tell(),
                None
            )
            # Remove old mock file
            os.remove(self.file.path)

            self.file = newfile
            self.save()
            self.generated = True


class ExpiringLink(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expire_in_seconds = models.PositiveIntegerField()
    expiration = models.DateTimeField(blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug_from_title(self.image.title)
        self.expiration = timezone.now() + timezone.timedelta(seconds=self.expire_in_seconds)
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if not self.expiration:
            return False
        return timezone.now() > self.expiration
