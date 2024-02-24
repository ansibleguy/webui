from os import listdir
from pathlib import Path
from functools import cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from aw.config.main import config
from aw.api_endpoints.base import API_PERMISSION, BaseResponse, GenericResponse
from aw.model.repository import Repository
from aw.execute.repository import get_path_repo_wo_isolate
from aw.utils.util import is_set


class FileSystemReadResponse(BaseResponse):
    files = serializers.ListSerializer(child=serializers.CharField())
    directories = serializers.ListSerializer(child=serializers.CharField())


class FileSystemExistsResponse(BaseResponse):
    exists = serializers.BooleanField()
    fstype = serializers.CharField()


class APIFsBrowse(APIView):
    http_method_names = ['get']
    serializer_class = FileSystemReadResponse
    permission_classes = API_PERMISSION

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
        description="This endpoint is mainly used for form auto-completion when selecting job-files",
        parameters=[
            OpenApiParameter(
                name='base', type=str, default='/', description='Relative directory to query',
                required=False,
            ),
        ],
    )
    def get(cls, request, repository: int = None):
        # pylint: disable=R0912
        browse_root = Path(config['path_play'])
        items = {'files': [], 'directories': []}

        if repository not in [None, 0, '0']:
            try:
                repository = Repository.objects.get(id=repository)
                if repository is None:
                    raise ObjectDoesNotExist

                if repository.rtype_name == 'Static':
                    browse_root = repository.static_path

                else:
                    if repository.git_isolate:
                        # do not validate as the repo does not exist..
                        all_valid = ['.*']
                        items['files'] = all_valid
                        items['directories'] = all_valid
                        return Response(items)

                    browse_root = get_path_repo_wo_isolate(repository)
                    if is_set(repository.git_playbook_base):
                        browse_root = browse_root / repository.git_playbook_base

            except ObjectDoesNotExist:
                return Response(data={'msg': 'Provided repository does not exist'}, status=404)

        if not browse_root.is_dir():
            return Response(data={'msg': f"Base directory '{browse_root}' does not exist"}, status=404)

        if 'base' not in request.GET:
            base = '/'
        else:
            base = str(request.GET['base'])

        if base.find('..') != -1:
            return Response(data={'msg': 'Traversal not allowed'}, status=403)

        browse_root = browse_root / base

        if not browse_root.is_dir():
            return Response(data={'msg': f"Base directory '{browse_root}' does not exist"}, status=404)

        raw_items = cls._listdir(browse_root)

        for item in raw_items:
            try:
                item_path = browse_root / item
                if item_path.is_file():
                    items['files'].append(item)
                elif item_path.is_dir():
                    items['directories'].append(item)

            except OSError:
                continue

        return Response(items)


class APIFsExists(APIView):
    http_method_names = ['get']
    serializer_class = FileSystemExistsResponse
    permission_classes = API_PERMISSION

    @classmethod
    @extend_schema(
        request=None,
        responses={
            200: FileSystemExistsResponse,
            400: OpenApiResponse(GenericResponse, description='No file or directory not provided'),
            403: OpenApiResponse(GenericResponse, description='Access to file or directory is forbidden'),
        },
        summary='Return if the provided file or directory exists.',
        description="This endpoint is mainly used for form validation when configuring path and files",
        parameters=[
            OpenApiParameter(
                name='item', type=str, default=None, required=True,
                description='File or directory that should be checked',
            ),
        ],
    )
    def get(cls, request):
        if 'item' not in request.GET:
            return Response(data={'msg': "Required parameter 'item' was not provided"}, status=400)

        try:
            fs_item = Path(request.GET['item'])
            try:
                return Response({
                    'exists': fs_item.exists(),
                    'fstype': 'file' if fs_item.is_file() else 'directory',
                })

            except OSError:
                return Response({'exists': False, 'fstype': 'unknown'})

        except PermissionError:
            return Response(data={'msg': 'Access to file or directory is forbidden'}, status=403)
