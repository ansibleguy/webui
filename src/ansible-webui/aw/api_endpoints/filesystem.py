from os import listdir
from os import path as os_path
from pathlib import Path
from functools import cache

from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.config.main import config
from aw.api_endpoints.base import API_PERMISSION, BaseResponse, GenericResponse


class FileSystemReadResponse(BaseResponse):
    files = serializers.ListSerializer(child=serializers.CharField())
    directories = serializers.ListSerializer(child=serializers.CharField())


class APIFsBrowse(APIView):
    http_method_names = ['get']
    serializer_class = FileSystemReadResponse
    permission_classes = API_PERMISSION
    BROWSE_SELECTORS = {
        'playbook_file': config['path_play'],
        'inventory_file': config['path_play'],
    }

    @staticmethod
    @cache
    def _listdir(path: str) -> list[str]:
        return listdir(path)

    @classmethod
    @extend_schema(
        request=None,
        responses={
            200: FileSystemReadResponse,
            400: OpenApiResponse(GenericResponse, description='Invalid browse-selector provided'),
            403: OpenApiResponse(GenericResponse, description='Traversal not allowed'),
            404: OpenApiResponse(GenericResponse, description='Base directory does not exist'),
        },
        summary='Return list of existing files and directories.',
        description="This endpoint is mainly used for form auto-completion when selecting job-files. "
                    f"Available selectors are: {BROWSE_SELECTORS}"
    )
    def get(cls, request, selector: str):
        if selector not in cls.BROWSE_SELECTORS:
            return Response(data={'msg': 'Invalid browse-selector provided'}, status=400)

        if 'base' not in request.GET:
            base = '/'
        else:
            base = str(request.GET['base'])

        if not base.startswith('/'):
            base = f'/{base}'

        if base.find('..') != -1:
            return Response(data={'msg': 'Traversal not allowed'}, status=403)

        path_check = cls.BROWSE_SELECTORS[selector] + base
        if not Path(path_check).is_dir():
            return Response(data={'msg': 'Base directory does not exist'}, status=404)

        items = {'files': [], 'directories': []}
        raw_items = cls._listdir(path_check)

        for item in raw_items:
            item_path = Path(os_path.join(path_check, item))
            if item_path.is_file():
                items['files'].append(item)
            elif item_path.is_dir():
                items['directories'].append(item)

        return Response(items)
