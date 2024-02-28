from threading import Thread
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from aw.model.repository import Repository
from aw.api_endpoints.base import API_PERMISSION, GenericResponse, get_api_user, LogDownloadResponse
from aw.utils.permission import has_manager_privileges, has_repository_permission, get_viewable_repositories
from aw.model.job import Job
from aw.utils.util import unset_or_null, is_set
from aw.model.permission import CHOICE_PERMISSION_READ, CHOICE_PERMISSION_WRITE, CHOICE_PERMISSION_DELETE, \
    CHOICE_PERMISSION_EXECUTE
from aw.execute.repository import api_update_repository
from aw.api_endpoints.job_util import get_log_file_content


class RepositoryWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = Repository.api_fields_write


class RepositoryReadResponse(RepositoryWriteRequest):
    class Meta:
        model = Repository
        fields = Repository.api_fields_read

    rtype_name = serializers.CharField()
    status_name = serializers.CharField()
    log_stdout_url = serializers.CharField()
    log_stderr_url = serializers.CharField()


def repository_in_use(repository: Repository) -> bool:
    return Job.objects.filter(repository=repository).exists()


def validate_repository_types(repository: dict) -> (bool, str):
    rtype_name = Repository.rtype_name_from_id(repository['rtype'])
    if rtype_name == 'Git':
        try:
            if is_set(repository['git_override_initialize']) and is_set(repository['git_override_update']):
                return True, ''

        except KeyError:
            pass

        if unset_or_null(repository, 'git_origin'):
            return False, 'Git Origin is required'

        if unset_or_null(repository, 'git_branch'):
            return False, 'Git Branch is required'

    else:
        if unset_or_null(repository, 'static_path'):
            return False, 'Static Path is required'

    return True, ''


def build_repository(repository: Repository) -> dict:
    data = RepositoryReadResponse(instance=repository).data
    data['time_update'] = repository.time_update_str
    if data['log_stderr'] is None or not Path(data['log_stderr']).is_file():
        data['log_stderr'] = None
        data['log_stderr_url'] = None

    return data


class APIRepository(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = RepositoryReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: RepositoryReadResponse},
        summary='Return list of repositories',
        operation_id='repository_list',
    )
    def get(request):
        user = get_api_user(request)
        repositories = []

        for repository in get_viewable_repositories(user=user):
            repositories.append(build_repository(repository))

        return Response(data=repositories, status=200)

    @extend_schema(
        request=RepositoryWriteRequest,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='Repository created'),
            400: OpenApiResponse(response=GenericResponse, description='Invalid repository data provided'),
            403: OpenApiResponse(response=GenericResponse, description='Not privileged to create a repository'),
        },
        summary='Create a new Repository.',
        operation_id='repository_create',
    )
    def post(self, request):
        privileged = has_manager_privileges(user=get_api_user(request), kind='repository')
        if not privileged:
            return Response(data={'msg': 'Not privileged to manage repositories'}, status=403)

        serializer = RepositoryWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(data={'msg': f"Provided repository data is not valid: '{serializer.errors}'"}, status=400)

        rtype_valid, rtype_error = validate_repository_types(serializer.validated_data)
        if not rtype_valid:
            return Response(data={'msg': f"Provided repository data is not valid: '{rtype_error}'"}, status=400)

        try:
            serializer.save()

        except IntegrityError as err:
            return Response(data={'msg': f"Provided repository data is not valid: '{err}'"}, status=400)

        return Response({'msg': f"Repository '{serializer.data['name']}' created successfully"})


class APIRepositoryItem(GenericAPIView):
    http_method_names = ['get', 'put', 'post', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: RepositoryReadResponse,
            404: OpenApiResponse(response=GenericResponse, description='Repository does not exist'),
        },
        summary='Return information of a repository.',
        operation_id='repository_get'
    )
    def get(request, repo_id: int):
        user = get_api_user(request)

        try:
            repository = Repository.objects.get(id=repo_id)
            if not has_repository_permission(
                    user=user,
                    repository=repository,
                    permission_needed=CHOICE_PERMISSION_READ
            ):
                return Response(
                    data={'msg': f"Not privileged to view the repository '{repository.name}'"},
                    status=403,
                )

            return Response(data=build_repository(repository), status=200)

        except ObjectDoesNotExist:
            return Response(data={'msg': f"Repository with ID {repo_id} does not exist"}, status=404)

    @extend_schema(
        request=RepositoryWriteRequest,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='Repository updated'),
            400: OpenApiResponse(response=GenericResponse, description='Invalid repository data provided'),
            403: OpenApiResponse(response=GenericResponse, description='Not privileged to edit the repository'),
            404: OpenApiResponse(response=GenericResponse, description='Repository does not exist'),
        },
        summary='Modify a repository.',
        operation_id='repository_edit',
    )
    def put(self, request, repo_id: int):
        user = get_api_user(request)

        serializer = RepositoryWriteRequest(data=request.data)
        if not serializer.is_valid():
            return Response(data={'msg': f"Provided repository data is not valid: '{serializer.errors}'"}, status=400)

        rtype_valid, rtype_error = validate_repository_types(serializer.validated_data)
        if not rtype_valid:
            return Response(data={'msg': f"Provided repository data is not valid: '{rtype_error}'"}, status=400)

        try:
            repository = Repository.objects.get(id=repo_id)

        except ObjectDoesNotExist:
            repository = None

        if repository is None:
            return Response(data={'msg': f"Repository with ID {repo_id} does not exist"}, status=404)

        if not has_repository_permission(
                user=user,
                repository=repository,
                permission_needed=CHOICE_PERMISSION_WRITE
        ):
            return Response(
                data={'msg': f"Not privileged to modify the repository '{repository.name}'"},
                status=403,
            )

        try:
            Repository.objects.filter(id=repo_id).update(**serializer.data)
            return Response(data={'msg': f"Repository '{repository.name}' updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'msg': f"Provided repository data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='Repository deleted'),
            400: OpenApiResponse(response=GenericResponse, description='Invalid repository data provided'),
            403: OpenApiResponse(response=GenericResponse, description='Not privileged to delete the repository'),
            404: OpenApiResponse(response=GenericResponse, description='Repository does not exist'),
        },
        summary='Delete a repository.',
        operation_id='repository_delete'
    )
    def delete(self, request, repo_id: int):
        user = get_api_user(request)

        try:
            repository = Repository.objects.get(id=repo_id)
            if repository is not None:
                if not has_repository_permission(
                        user=user,
                        repository=repository,
                        permission_needed=CHOICE_PERMISSION_DELETE
                ):
                    return Response(
                        data={'msg': f"Not privileged to delete the repository '{repository.name}'"},
                        status=403,
                    )

                if repository_in_use(repository):
                    return Response(
                        data={'msg': f"Repository '{repository.name}' cannot be deleted as it is still in use"},
                        status=400,
                    )

                repository.delete()
                return Response(data={'msg': f"Repository '{repository.name}' deleted"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Repository with ID {repo_id} does not exist"}, status=404)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='Repository update initiated'),
            403: OpenApiResponse(response=GenericResponse, description='Not privileged to update the repository'),
            404: OpenApiResponse(response=GenericResponse, description='Repository does not exist'),
        },
        summary='Download/Update a repository.',
        operation_id='repository_update'
    )
    def post(self, request, repo_id: int):
        user = get_api_user(request)

        try:
            repository = Repository.objects.get(id=repo_id)
            if repository is not None:
                if not has_repository_permission(
                        user=user,
                        repository=repository,
                        permission_needed=CHOICE_PERMISSION_EXECUTE,
                ):
                    return Response(
                        data={'msg': f"Not privileged to update the repository '{repository.name}'"},
                        status=403,
                    )

                repository_update_thread = Thread(
                    target=api_update_repository,
                    kwargs={'repository': repository, 'user': user}
                )
                repository_update_thread.start()

                return Response(data={'msg': f"Repository '{repository.name}' update initiated"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Repository with ID {repo_id} does not exist"}, status=404)


class APIRepositoryLogFile(GenericAPIView):
    http_method_names = ['get']
    serializer_class = LogDownloadResponse
    permission_classes = API_PERMISSION
    valid_logfile_type = ['stdout', 'stderr']

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(GenericResponse, description='Download repository log-file'),
            403: OpenApiResponse(GenericResponse, description='Not privileged to view the repository logs'),
            404: OpenApiResponse(GenericResponse, description='Repository or log-file dos not exist'),
        },
        summary='Download log-file of the last repository update.',
        operation_id='repository_logfile',
        parameters=[
            OpenApiParameter(
                name='type', type=str, default='stdout',
                description=f"Type of log-file to download. One of {valid_logfile_type}",
                required=False,
            ),
        ],
    )
    def get(self, request, repo_id: int):
        user = get_api_user(request)
        try:
            repository = Repository.objects.get(id=repo_id)
            if repository is not None:
                if not has_repository_permission(
                        user=user,
                        repository=repository,
                        permission_needed=CHOICE_PERMISSION_READ,
                ):
                    return Response(
                        data={'msg': f"Not privileged to view logs of the repository '{repository.name}'"},
                        status=403,
                    )

                logfile = repository.log_stdout
                if 'type' in request.GET:
                    logfile_type = request.GET['type'] if request.GET['type'] in self.valid_logfile_type else 'stdout'
                    logfile = getattr(repository, f'log_{logfile_type}')

                if logfile is None:
                    return Response(data={'msg': f"No logs found for repository '{repository.name}'"}, status=404)

                return get_log_file_content(logfile)

        except (ObjectDoesNotExist, FileNotFoundError):
            pass

        return Response(
            data={'msg': f"Repository with ID '{repo_id}' or log-file does not exist"},
            status=404,
        )
