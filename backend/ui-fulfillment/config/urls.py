from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/', include('fulfillment_service.wallets.urls')),
    path('api/v1/', include('fulfillment_service.assets.urls')),
]

if settings.ADMIN_ENABLED:
    from django.contrib import admin

    urlpatterns = [path(settings.ADMIN_URL, admin.site.urls)] + urlpatterns

if settings.DEBUG:
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view
    from rest_framework import permissions

    api_info = openapi.Info(
        title='Google Pattern API',
        default_version='v1',
        description='An API for the backend of Google Pattern project to provide functionality '
        'around financial advices, assets, transactions, and more.',
    )
    schema_view = get_schema_view(api_info, public=True, permission_classes=(permissions.AllowAny,))
    urlpatterns = [path('swagger/', schema_view.with_ui('swagger', cache_timeout=0))] + urlpatterns

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
