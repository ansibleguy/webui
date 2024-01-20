from time import time
from typing import Callable

from django.core.exceptions import ObjectDoesNotExist
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, extend_schema

from aw.model.api import APIKey
from aw.utils.http import deny_request


def endpoint_wrapper(func) -> Callable:
    def wrapper(request, *args, **kwargs):
        bad, deny = deny_request(request)
        if bad:
            return deny

        return func(request, *args, **kwargs)

    return wrapper


class KeyRead(APIView):
    http_method_names = ['get']

    @staticmethod
    @endpoint_wrapper
    @extend_schema(
        summary='Return a list of all existing API keys of the current user.',
        parameters=None,
    )
    def get(request):
        return Response({'tokens': [key.name for key in APIKey.objects.filter(user=request.user)]})


class KeyWrite(APIView):
    http_method_names = ['post', 'delete']

    @staticmethod
    @endpoint_wrapper
    @extend_schema(
        summary='Create a new API key.',
    )
    def post(request):
        token, secret = APIKey.objects.create_key(
            name=f'{request.user}-{time()}',
            user=request.user,
        )
        return Response({'token': token, 'secret': secret})

    @staticmethod
    @endpoint_wrapper
    @extend_schema(
        summary='Delete one of the existing API keys of the current user.',
    )
    def delete(request):
        req_key = request.query_params.get('token', None)

        if req_key is None:
            return Response({'msg': 'No API key provided'})

        try:
            results = APIKey.objects.filter(user=request.user, name=req_key)
            if len(results) == 1:
                results.delete()
                return Response({'msg': f"API key '{req_key}' revoked"})

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"API key '{req_key}' not found"}, status=404)


urlpatterns_api = [
    path('api/key', KeyRead.as_view()),
    path('api/key/<str:token>', KeyWrite.as_view()),
    path('api/_schema/', SpectacularAPIView.as_view(), name='_schema'),
    path('api', SpectacularSwaggerView.as_view(url_name='_schema'), name='swagger-ui'),
]
