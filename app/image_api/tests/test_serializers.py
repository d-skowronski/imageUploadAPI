from core.models import Tier
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory

from ..models import Image
from ..serializers import UploadedImageSerializer
from . import FileTestCase

User = get_user_model()


class UploadedImageSerializerTestCase(FileTestCase):
    def setUp(self):
        self.tiers = {
            'basic': Tier.objects.get(original_link_access=False, expiring_link_generation_access=False),
            'premium': Tier.objects.get(original_link_access=True, expiring_link_generation_access=False),
            'enterprise': Tier.objects.get(original_link_access=True, expiring_link_generation_access=True),
        }
        self.user = User.objects.create_user(username='testuser', password='testpassword', tier=self.tiers['basic'])
        self.image_file = SimpleUploadedFile('test_image.jpg', b'file_content')
        self.image = Image.objects.create(
            file=self.image_file,
            uploader=self.user
        )
        self.request = APIRequestFactory().request()
        self.request.user = self.user

    def test_serialization(self):
        serializer = UploadedImageSerializer(instance=self.image, context={'request': self.request})
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            set(['pk', 'title', 'file_urls', 'expiring_link_generator', 'uploaded_at'])
        )

    def test_serialization_basic_tier(self):
        self.user.tier = self.tiers['basic']
        self.user.save()

        serializer = UploadedImageSerializer(instance=self.image, context={'request': self.request})
        data = serializer.data

        self.assertEqual(len(data['file_urls']), 1)
        self.assertIsNotNone(data['file_urls'].get('200 px high'))
        self.assertEqual(data['expiring_link_generator'], '')

    def test_serialization_premium_tier(self):
        self.user.tier = self.tiers['premium']
        self.user.save()

        serializer = UploadedImageSerializer(instance=self.image, context={'request': self.request})
        data = serializer.data

        self.assertEqual(len(data['file_urls']), 3)
        self.assertIsNotNone(data['file_urls'].get('200 px high'))
        self.assertIsNotNone(data['file_urls'].get('400 px high'))
        self.assertIsNotNone(data['file_urls'].get('original'))
        self.assertEqual(data['expiring_link_generator'], '')

    def test_serialization_enterprise_tier(self):
        self.user.tier = self.tiers['enterprise']
        self.user.save()

        serializer = UploadedImageSerializer(instance=self.image, context={'request': self.request})
        data = serializer.data

        self.assertEqual(len(data['file_urls']), 3)
        self.assertIsNotNone(data['file_urls'].get('200 px high'))
        self.assertIsNotNone(data['file_urls'].get('400 px high'))
        self.assertIsNotNone(data['file_urls'].get('original'))
        self.assertNotEqual(data['expiring_link_generator'], '')

    def test_deserialization(self):
        data = {
            'file': self.image_file,
        }

        serializer = UploadedImageSerializer(data=data, context={'request': self.request})
        serializer.is_valid()
        image_object = serializer.save()

        self.assertIsInstance(image_object, Image)
        self.assertEqual(image_object.uploader, self.user)

    def test_deserialization_invalid_extension(self):
        invalid_image_file = SimpleUploadedFile('test_image.invalid_extenson', b'file_content')
        data = {
            'file': invalid_image_file,
        }
        serializer = UploadedImageSerializer(data=data, context={'request': self.request})

        self.assertFalse(serializer.is_valid())
