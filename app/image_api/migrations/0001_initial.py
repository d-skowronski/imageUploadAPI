# Generated by Django 4.2.5 on 2023-09-20 07:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('file', models.ImageField(upload_to='original')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResizedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('file', models.ImageField(blank=True, null=True, upload_to='resized')),
                ('height', models.PositiveIntegerField()),
                ('generated', models.BooleanField(default=False)),
                ('original', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resizes', to='image_api.image')),
            ],
        ),
        migrations.CreateModel(
            name='ExpiringLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('expiration', models.DateTimeField()),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_api.image')),
            ],
        ),
    ]