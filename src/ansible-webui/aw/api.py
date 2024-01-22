from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from aw.api_endpoints.key import APIKey, APIKeyItem
from aw.api_endpoints.job import APIJob, APIJobItem

urlpatterns_api = [
    path('api/key/<str:token>', APIKeyItem.as_view()),
    path('api/key', APIKey.as_view()),
    path('api/job/<int:job_id>', APIJobItem.as_view()),
    path('api/job', APIJob.as_view()),
    path('api/_schema/', SpectacularAPIView.as_view(), name='_schema'),
    path('api/_docs', SpectacularSwaggerView.as_view(url_name='_schema'), name='swagger-ui'),
]
