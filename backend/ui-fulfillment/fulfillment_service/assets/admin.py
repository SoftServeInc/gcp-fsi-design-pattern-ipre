from django.contrib import admin

from .models import Asset, Metrics

admin.site.register(Asset)
admin.site.register(Metrics)
