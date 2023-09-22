from core.models import Tier
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.test import Client
from image_api.models import Image
from image_api.tests import FileTestCase, generate_image


class ImageViewTestCase(FileTestCase):
    '''
    Extends FileTestCase. Sets up:
    - self.client - Client for making requests
    - self.original_image - Sample original image of the Image model
    - self.user - Uploader of the original_image
    '''
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            tier=Tier.objects.get(thumbnailHeights=[200])
        )
        self.client = Client()

        self.original_image = Image.objects.create(
            file=ImageFile(
                file=generate_image(),
                name="test_image.png"
            ),
            uploader=self.user
        )
