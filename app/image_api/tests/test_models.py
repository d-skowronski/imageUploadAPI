from datetime import timedelta
from io import BytesIO
from os.path import basename
from unittest.mock import patch
from PIL import Image as PIL_Image
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from ..models import Image, ResizedImage, ExpiringLink
from . import FileTestCase


def generate_image(size=500, color=(256, 0, 0), format='png'):
    '''Create image in memory
    Default: 500x500px all red png image
    '''
    image_buffer = BytesIO()
    image = PIL_Image.new('RGBA', size=(size, size), color=color)
    image.save(image_buffer, format)
    return ImageFile(image_buffer)


class ImageTestCase(FileTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_creation(self):
        time = timezone.now()
        image = Image.objects.create(
            file=SimpleUploadedFile("test_image.jpg", b"file_content"),
            uploader=self.user
        )

        self.assertAlmostEqual(image.uploaded_at, time, delta=timedelta(seconds=1))
        self.assertIsNotNone(image.file)
        self.assertEqual(image.uploader, self.user)

    @patch('image_api.models.generate_slug_from_title', lambda x: 'mock_slug')
    def test_save(self):
        image = Image.objects.create(
            file=SimpleUploadedFile("test_image.jpg", b"file_content"),
            uploader=self.user
        )

        self.assertEqual(image.title, "test_image")
        self.assertEqual(image.slug, 'mock_slug')
        self.assertEqual(basename(image.file.name), 'mock_slug' + '.jpg')

    def test_upload_path(self):
        self.assertEqual(Image.file.field.upload_to, 'original')


class ResizedImageTestCase(FileTestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

        self.original_image = Image.objects.create(
            file=ImageFile(
                file=generate_image(),
                name="test_image.jpg"
            ),
            uploader=self.user
        )

    def test_creation(self):
        resize = ResizedImage.objects.create(
            original=self.original_image,
            height=500,
        )

        self.assertEqual(resize.original, self.original_image)
        self.assertEqual(resize.height, 500)
        self.assertFalse(resize.generated)

    def test_creation_height_negative(self):
        with self.assertRaises(ValidationError):
            ResizedImage.objects.create(
                original=self.original_image,
                height=-100,
            )

    def test__generate_mock_file(self):
        resize = ResizedImage.objects.create(
            original=self.original_image,
            height=100,
            slug='test_slug'
        )
        resize._generate_mock_file()

        self.assertIsNotNone(resize.file)
        self.assertEqual(resize.file.name, resize.slug + '.jpg')

    @patch('image_api.models.ResizedImage._generate_mock_file')
    @patch('image_api.models.generate_slug_from_title', lambda x: 'mock_slug')
    def test_save(self, patch_generate_mock_file):
        resize = ResizedImage.objects.create(
            original=self.original_image,
            height=100,
        )

        self.assertEqual(resize.slug, 'mock_slug')
        self.assertEqual(patch_generate_mock_file.call_count, 1)

        resize.height = -100
        with self.assertRaises(ValidationError):
            resize.save()

    @patch('image_api.models.ResizedImage.generate_resized_image')
    def test_resized_file_generated(self, patch_generate_resized_image):
        resize = ResizedImage.objects.create(
            original=self.original_image,
            height=100,
            generated=True
        )

        self.assertEqual(resize.resized_file, resize.file)
        self.assertEqual(patch_generate_resized_image.call_count, 0)

    @patch('image_api.models.ResizedImage.generate_resized_image')
    def test_resized_file_not_generated(self, patch_generate_resized_image):
        resize = ResizedImage.objects.create(
            original=self.original_image,
            height=100,
        )

        self.assertEqual(resize.resized_file, resize.file)
        self.assertEqual(patch_generate_resized_image.call_count, 1)

    def test_generate_resized_image(self):
        resize = ResizedImage.objects.create(
            original=self.original_image,
            height=100,
        )
        mock_file_name = resize.file.name
        resize.generate_resized_image()

        self.assertEqual(resize.file.height, resize.height)
        self.assertEqual(resize.file.name, mock_file_name)


class ExpiringLinkTestCase(FileTestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

        self.original_image = Image.objects.create(
            file=ImageFile(
                file=generate_image(),
                name="test_image.png"
            ),
            uploader=self.user
        )

    def test_creation(self):
        link = ExpiringLink(image=self.original_image, valid_for=5)

        self.assertEqual(link.image, self.original_image)
        self.assertEqual(link.valid_for, 5)
        self.assertFalse(link.is_expired)
        self.assertIsNone(link.expiration)

    def test_save(self):
        link = ExpiringLink.objects.create(
            image=self.original_image,
            valid_for=5
        )

        self.assertAlmostEqual(
            link.expiration,
            timezone.now() + timezone.timedelta(seconds=link.valid_for),
            delta=timedelta(milliseconds=500)
        )
        self.assertFalse(link.is_expired)

    @patch('image_api.models.timezone.now')
    def test_is_expired(self, time_now_mock):
        # Make aware not necessary, it just prevents warning from django
        time_now_mock.return_value = timezone.make_aware(datetime(2023, 9, 22))
        link = ExpiringLink.objects.create(
            image=self.original_image,
            valid_for=5
        )

        # Move time in future...
        time_now_mock.return_value = timezone.make_aware(datetime(2023, 9, 22, second=link.valid_for+1))

        self.assertTrue(link.is_expired)
