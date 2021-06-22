import os
from django.conf import settings

APPS_DIR = settings.APPS_DIR


def load_statements(path):
    return open(os.path.join(APPS_DIR, path)).read()