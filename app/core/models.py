from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Tier(models.Model):
    name = models.CharField(max_length=128, blank=False, unique=True)
    thumbnailHeights = ArrayField(models.IntegerField())
    original_link_access = models.BooleanField(default=False)
    expiring_link_generation_access = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.name)


class User(AbstractUser):
    # Migration '0002_auto_20230914_1302' adds initial Tiers. Pk 1 corresponds to default Tier
    tier = models.ForeignKey(Tier, on_delete=models.PROTECT, default=1, blank=False)

    def __str__(self) -> str:
        return str(self.username)
