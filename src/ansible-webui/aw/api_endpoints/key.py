from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.utils.util import datetime_w_tz
from aw.config.hardcoded import KEY_TIME_FORMAT
from aw.model.api import AwAPIKey
from aw.api_endpoints.base import API_PERMISSION, get_api_user


# todo: allow user to add comment to easier identify token
class KeyReadResponse(serializers.Serializer):
    tokens = serializers.ListSerializer(child=serializers.CharField())


class KeyWriteResponse(serializers.Serializer):
    token = serializers.CharField()
    secret = serializers.CharField()


class KeyReadWrite(APIView):
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
        return Response({'tokens': [key.name for key in AwAPIKey.objects.filter(user=get_api_user(request))]})

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(KeyWriteResponse, description='Returns generated API token & key')},
        summary='Create a new API key.',
    )
    def post(self, request):
        self.serializer_class = KeyWriteResponse
        user = get_api_user(request)
        token = f'{user}-{datetime_w_tz().strftime(KEY_TIME_FORMAT)}'
        _, key = AwAPIKey.objects.create_key(
            name=token,
            user=user,
        )
        return Response({'token': token, 'key': key})


class KeyDeleteResponse(serializers.Serializer):
    msg = serializers.CharField()


class KeyDelete(APIView):
    http_method_names = ['post', 'delete']
    serializer_class = KeyDeleteResponse
    permission_classes = API_PERMISSION
    _schema_responses = {
        200: OpenApiResponse(response=KeyDeleteResponse, description='API key deleted'),
        404: OpenApiResponse(response=KeyDeleteResponse, description='API key does not exist'),
    }
    _schema_summary = 'Delete one of the existing API keys of the current user.'

    @extend_schema(
        request=None,
        responses=_schema_responses,
        summary=_schema_summary,
    )
    def delete(self, request, token: str):
        try:
            results = AwAPIKey.objects.filter(user=get_api_user(request), name=token)

            if len(results) == 1:
                results.delete()
                return Response({'msg': f"API key '{token}' deleted"})

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"API key '{token}' not found"}, status=404)

    @extend_schema(
        request=None,
        responses=_schema_responses,
        summary=_schema_summary,
        operation_id='del',
    )
    def post(self, request, token: str):
        return self.delete(request, token)
