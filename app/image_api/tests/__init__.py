from shutil import rmtree
from django.test import TestCase, override_settings

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
