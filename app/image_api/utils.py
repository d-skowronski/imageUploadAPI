from django.utils.text import slugify
import uuid


def generate_slug_from_title(title):
    return f'{slugify(title[:10] if title else "")}-{uuid.uuid4()}'
