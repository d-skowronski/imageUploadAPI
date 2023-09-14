from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from ..models import Tier
User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.default_tier, _ = Tier.objects.get_or_create(
            name='Basic',
        )

    def test_creation(self):
        user = User.objects.create_user(username='test', password='test')

        self.assertIsInstance(user, User)
        self.assertEqual(user.tier, self.default_tier)

    def test_str(self):
        user = User.objects.create_user(username='test', password='test')

        self.assertEqual(user.username, str(user))


class TierTestCase(TestCase):
    def test_creation(self):
        tier = Tier(name='test', thumbnailHeights=[1, 2])

        self.assertIsInstance(tier, Tier)
        self.assertEqual(tier.name, 'test')
        self.assertCountEqual(tier.thumbnailHeights, [1, 2])
        self.assertFalse(tier.original_link_access)
        self.assertFalse(tier.expiring_link_generation_access)

    def test_unique_name_requirement(self):
        tier_1 = Tier(name='test', thumbnailHeights=[])
        tier_1.save()
        tier_2 = Tier(name='test', thumbnailHeights=[])

        with self.assertRaises(IntegrityError):
            tier_2.save()

    def test_max_name_length(self):
        self.assertEqual(Tier._meta.get_field('name').max_length, 128)

    def test_str(self):
        tier = Tier(name='test', thumbnailHeights=[1, 2])

        self.assertEqual(tier.name, str(tier))

    def test_initial_tiers_count(self):
        tiers = Tier.objects.all()

        self.assertEqual(len(tiers), 3)

    def test_default_initial_tier(self):
        tier = Tier.objects.get(pk=1)

        self.assertEqual(tier.name, 'Basic')
        self.assertCountEqual(tier.thumbnailHeights, [200])
        self.assertFalse(tier.original_link_access)
        self.assertFalse(tier.expiring_link_generation_access)

    def test_premium_initial_tier(self):
        tier = Tier.objects.get(name='Premium')

        self.assertCountEqual(tier.thumbnailHeights, [200, 400])
        self.assertTrue(tier.original_link_access)
        self.assertFalse(tier.expiring_link_generation_access)

    def test_enterprise_initial_tier(self):
        tier = Tier.objects.get(name='Enterprise')

        self.assertCountEqual(tier.thumbnailHeights, [200, 400])
        self.assertTrue(tier.original_link_access)
        self.assertTrue(tier.expiring_link_generation_access)
