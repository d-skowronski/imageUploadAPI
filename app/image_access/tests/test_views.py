from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch
from image_api.models import ResizedImage, ExpiringLink
from . import ImageViewTestCase


class OriginalImageViewTestCase(ImageViewTestCase):
    def test_accessible(self):
        url = reverse('original_link', args=[self.original_image.slug + '.png'])
        self.user.tier.original_link_access = True
        self.user.tier.save()
        response = self.client.get(url)

        with self.original_image.file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, image_content)

    def test_not_found(self):
        url = reverse('original_link', args=['non_existing_slug' + '.png'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_forbidden(self):
        url = reverse('original_link', args=[self.original_image.slug + '.png'])
        response = self.client.get(url)

        with self.original_image.file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(response.content, image_content)


class ResizedImageViewTestCase(ImageViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.resize = ResizedImage.objects.create(
            original=self.original_image,
            height=200,
        )

    def test_accessible(self):
        url = reverse('resized_link', args=[self.resize.slug + '.png'])
        response = self.client.get(url)
        with self.resize.resized_file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, image_content)

    def test_not_found(self):
        url = reverse('resized_link', args=['non_existing_slug' + '.png'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_forbidden(self):
        '''
        Test for case when original uploader tier changes and
        selected height is not avaliable
        '''
        url = reverse('resized_link', args=[self.resize.slug + '.png'])
        self.user.tier.thumbnailHeights = []
        self.user.tier.save()
        response = self.client.get(url)
        with self.resize.resized_file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(response.content, image_content)


class ExpiringLinkViewTestCase(ImageViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.expiring_link = ExpiringLink.objects.create(
            image=self.original_image,
            valid_for=30
        )

    def test_accessible(self):
        url = reverse('expiring_link', args=[self.expiring_link.pk])
        self.user.tier.expiring_link_generation_access = True
        self.user.tier.save()

        response = self.client.get(url)
        with self.expiring_link.image.file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, image_content)

    @patch('image_api.models.timezone.now')
    def test_expired(self, time_now_mock):
        time_now_mock.return_value = timezone.make_aware(
            datetime.now() + timedelta(seconds=self.expiring_link.valid_for+1)
        )
        url = reverse('expiring_link', args=[self.expiring_link.pk])
        self.user.tier.expiring_link_generation_access = True
        self.user.tier.save()

        response = self.client.get(url)
        with self.expiring_link.image.file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(response.content, image_content)

    def test_forbidden(self):
        url = reverse('expiring_link', args=[self.expiring_link.pk])
        response = self.client.get(url)
        with self.expiring_link.image.file.open() as file:
            image_content = file.read()

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(response.content, image_content)

    def test_not_found(self):
        url = reverse('expiring_link', args=['non_existing_pk'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
