from django.test import TestCase
from unittest.mock import patch
from ..utils import generate_slug_from_title

mock_uuid = 'mock_uuid'


@patch('image_api.utils.uuid.uuid4', lambda: mock_uuid)  # Make uuid4 deterministic
@patch('image_api.utils.slugify', lambda x: x)  # Make test independent of slugify implementation
class SlugFromTitleTestCase(TestCase):
    def test_valid_input(self):
        input = 'Test title'
        slug = generate_slug_from_title(input)

        self.assertEqual(slug, f'{input}-{mock_uuid}')

    def test_empty_input_str(self):
        slug = generate_slug_from_title('')

        self.assertEqual(slug, f'-{mock_uuid}')

    def test_long_input_str(self):
        slug = generate_slug_from_title('a'*11)
        self.assertEqual(slug, f'{"a"*10}-{mock_uuid}')
