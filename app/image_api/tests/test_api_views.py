from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from core.models import Tier
from ..models import Image, ExpiringLink
from . import FileTestCase
from ..api_views import ExpiringLinkCreateList

User = get_user_model()


class ImageAPITestCase(FileTestCase):
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


class ExpiringLinkAPITestCase(FileTestCase):
    def setUp(self):
        # Create user with expiring link permission
        self.user1 = User.objects.create_user(
            username='testuser',
            password='testpassword',
            tier=Tier.objects.filter(expiring_link_generation_access=True).first()
        )
        self.image_of_user1 = Image.objects.create(
            uploader=self.user1,
            file=SimpleUploadedFile('test_image_1.jpg', b'file_content')
        )
        self.expiring_for_image1 = ExpiringLink.objects.create(
            image=self.image_of_user1,
            valid_for=10
        )
        # Create user without expiring link permission
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword',
            tier=Tier.objects.filter(expiring_link_generation_access=False).first()
        )
        self.image_of_user2 = Image.objects.create(
            uploader=self.user2,
            file=SimpleUploadedFile('test_image_1.jpg', b'file_content')
        )
        self.expiring_for_image2 = ExpiringLink.objects.create(
            image=self.image_of_user2,
            valid_for=10
        )

        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)

        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

    def test_uploader_with_permissions(self):
        response = self.client1.get(f'/api/images/{self.image_of_user1.pk}/expiring_links')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_uploader_with_permissions(self):
        response = self.client1.get(f'/api/images/{self.image_of_user2.pk}/expiring_links')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_uploader_without_permissions(self):
        response = self.client2.get(f'/api/images/{self.image_of_user2.pk}/expiring_links')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_uploader_without_permissions(self):
        response = self.client2.get(f'/api/images/{self.image_of_user1.pk}/expiring_links')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_existing_with_permissions(self):
        image_pk_not_in_use = max(list(Image.objects.all().values_list('pk', flat=True)))+1
        response = self.client1.get(f'/api/images/{image_pk_not_in_use}/expiring_links')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_existing_without_permissions(self):
        image_pk_not_in_use = max(list(Image.objects.all().values_list('pk', flat=True)))+1
        response = self.client2.get(f'/api/images/{image_pk_not_in_use}/expiring_links')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
