from shutil import rmtree
from django.test import TestCase, override_settings
from io import BytesIO
from PIL import Image as PIL_Image
from django.core.files.images import ImageFile

TEST_DIR = 'test_data'


@override_settings(MEDIA_ROOT=(TEST_DIR + '/user_content'))
class FileTestCase(TestCase):
    '''
    Default Django's TestCase with extended functionality.

    Replaces setting MEDIA_ROOT to temporary folder and removes this folder after
    every test in class has been run.
    '''
    @classmethod
    def tearDownClass(cls):
        rmtree(TEST_DIR, ignore_errors=True)
        super().tearDownClass()


def generate_image(size=500, color=(256, 0, 0), format='png'):
    '''Create image in memory
    Default: 500x500px all red png image
    '''
    image_buffer = BytesIO()
    image = PIL_Image.new('RGBA', size=(size, size), color=color)
    image.save(image_buffer, format)
    return ImageFile(image_buffer)
