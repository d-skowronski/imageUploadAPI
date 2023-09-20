from shutil import rmtree

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Image
from . import TEST_DIR

User = get_user_model()


@override_settings(MEDIA_ROOT=(TEST_DIR + '/user_content'))
class ImageAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.image1 = Image.objects.create(
            uploader=self.user,
            file=SimpleUploadedFile('test_image_1.jpg', b'file_content')
        )
        self.image2 = Image.objects.create(
            uploader=self.user,
            file=SimpleUploadedFile('test_image_2.jpg', b'file_content')
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @classmethod
    def tearDownClass(cls):
        rmtree(TEST_DIR, ignore_errors=True)
        super().tearDownClass()

    def test_image_list_upload(self):
        '''Test ImageListUpload view (GET request)'''
        response = self.client.get('/api/images/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_image_create(self):
        '''Test ImageListUpload view (POST request)'''
        image_file = SimpleUploadedFile('test_image_3.png', content=b'file content', content_type='image/jpg')
        data = {'file': image_file}
        response = self.client.post('/api/images/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_image_detail(self):
        '''Test ImageDetail view (GET request)'''

        response = self.client.get(f'/api/images/{self.image1.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], self.image1.pk)

    def test_image_detail_with_unauthorized_user(self):
        '''Test the ImageDetail view with an user that did not upload (GET request)'''
        unauthorized_user = User.objects.create_user(username='another_user', password='testpassword')
        self.client.force_authenticate(user=unauthorized_user)
        response = self.client.get(f'/api/images/{self.image1.pk}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
