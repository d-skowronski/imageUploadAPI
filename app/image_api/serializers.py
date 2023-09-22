from rest_framework import serializers
from .models import Image, ResizedImage, ExpiringLink
from core.models import Tier
from django.core.validators import FileExtensionValidator
from django.conf import settings
from rest_framework.reverse import reverse


class ExpiringLinkSerializer(serializers.HyperlinkedModelSerializer):
    link = serializers.SerializerMethodField()

    class Meta:
        model = ExpiringLink
        fields = ('link', 'expiration', 'valid_for')

    def get_link(self, obj):
        request = self.context['request']
        return reverse('expiring_link', args=[obj.pk], request=request)

    def create(self, validated_data):
        validated_data['image'] = Image.objects.get(pk=self.context['image_pk'])
        return super().create(validated_data)


class UploadedImageSerializer(serializers.ModelSerializer):
    file_urls = serializers.SerializerMethodField()
    expiring_link_generator = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True, validators=[FileExtensionValidator(settings.ALLOWED_IMAGE_EXTENSIONS)])

    class Meta:
        model = Image
        fields = ('pk', 'title', 'file', 'file_urls', 'expiring_link_generator', 'uploaded_at')
        read_only_fields = ('title',)

    def get_file_urls(self, obj):
        '''Get all available urls based on uploader's tier'''
        request = self.context['request']
        # uploader_tier = obj.uploader.tier
        uploader_tier = Tier.objects.get(user__pk=obj.uploader_id)
        urls = {}

        # Original url
        if uploader_tier.original_link_access:
            original_url = request.build_absolute_uri(obj.file.url)
            urls['original'] = original_url

        # Resized urls - resizes creation logic is in here in case of uploader's tier change
        image_heights = set(uploader_tier.thumbnailHeights)
        resizes = obj.resizes.filter(height__in=image_heights)

        for resized_image in resizes:
            image_heights.remove(resized_image.height)
            urls[f'{resized_image.height} px high'] = request.build_absolute_uri(resized_image.file.url)

        # image_heights that have not been removed indicate that they are missing resizes
        # bulk_create could result here in less db hits, however there is custom logic in model's save() method
        # also, logic below will be ran only once for each resize
        for height in image_heights:
            resized_image = ResizedImage.objects.create(height=height, original=obj)
            urls[f'{height} px high'] = request.build_absolute_uri(resized_image.file.url)

        return urls

    def get_expiring_link_generator(self, obj):
        request = self.context['request']
        uploader_tier = obj.uploader.tier
        link_generator = ''
        if uploader_tier.expiring_link_generation_access:
            link_generator = reverse('expiring_link_manager', request=request, args=[obj.pk])

        return link_generator

    def create(self, validated_data):
        # Current user is added
        validated_data['uploader'] = self.context['request'].user

        image = Image.objects.create(**validated_data)
        image.full_clean()
        return image
