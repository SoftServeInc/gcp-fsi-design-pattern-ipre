import datetime
import threading
from concurrent import futures
from decimal import Decimal

import requests
from django.conf import settings

DECIMAL_PLACES = settings.DECIMAL_PLACES
thread_local = threading.local()


def date_to_timestamp(date):
    return int(datetime.datetime.combine(date, datetime.time()).timestamp())


def decimal_from_str(value):
    if value:
        value = round(Decimal(value), DECIMAL_PLACES)
    return value


def get_concurrent(func, values):
    with futures.ThreadPoolExecutor() as executor:
        return executor.map(func, values)


def requests_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session
