#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

import django
from django.contrib.auth import get_user_model


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # This allows easy placement of apps within the interior
    # fulfillment_service directory.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "fulfillment_service"))

    if 'createsuperuser' in sys.argv:
        django.setup()
        UserModel = get_user_model()
        parser = ArgumentParser()
        parser.add_argument('--{}'.format(UserModel.USERNAME_FIELD))
        args, unknown = parser.parse_known_args(sys.argv)
        username = args.username

        if username and UserModel.objects.filter(username=username).exists():
            print('Superuser exists')
        else:
            execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
