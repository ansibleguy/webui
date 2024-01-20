from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from aw.api_endpoints.key import KeyReadWrite, KeyDelete
from aw.api_endpoints.job import JobListCreate, JobViewEditDelete

urlpatterns_api = [
    path('api/key', KeyReadWrite.as_view()),
    path('api/key/<str:token>', KeyDelete.as_view()),
    path('api/job', JobListCreate.as_view()),
    path('api/job/<int:job_id>', JobViewEditDelete.as_view()),
    path('api/_schema/', SpectacularAPIView.as_view(), name='_schema'),
    path('api/_docs', SpectacularSwaggerView.as_view(url_name='_schema'), name='swagger-ui'),
]
