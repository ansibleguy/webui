from hashlib import md5

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.utils.util import datetime_w_tz
from aw.config.hardcoded import KEY_TIME_FORMAT
from aw.model.api import AwAPIKey
from aw.api_endpoints.base import API_PERMISSION, get_api_user, BaseResponse, GenericResponse


class KeyReadResponse(BaseResponse):
    token = serializers.CharField()
    id = serializers.CharField()


class KeyWriteResponse(BaseResponse):
    token = serializers.CharField()
    secret = serializers.CharField()


class APIKey(APIView):
    http_method_names = ['post', 'get']
    serializer_class = KeyReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: KeyReadResponse},
        summary='Return a list of all existing API keys of the current user.',
    )
    def get(request):
        tokens = []
        for key in AwAPIKey.objects.filter(user=get_api_user(request)):
            tokens.append({'token': key.name, 'id': md5(key.name.encode('utf-8')).hexdigest()})

        return Response(tokens)

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(KeyWriteResponse, description='Returns generated API token & key')},
        summary='Create a new API key.',
    )
    def post(self, request):
        self.serializer_class = KeyWriteResponse
        user = get_api_user(request)
        token = f'{user}-{datetime_w_tz().strftime(KEY_TIME_FORMAT)}'
        _, key = AwAPIKey.objects.create_key(name=token, user=user)
        return Response({'token': token, 'key': key})


class APIKeyItem(APIView):
    http_method_names = ['delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='API key deleted'),
            404: OpenApiResponse(response=GenericResponse, description='API key does not exist'),
        },
        summary='Delete one of the existing API keys of the current user.',
    )
    def delete(self, request, token: str):
        try:
            result = AwAPIKey.objects.get(user=get_api_user(request), name=token)

            if result is not None:
                result.delete()
                return Response(data={'msg': 'API key deleted'}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': 'API key not found'}, status=404)
