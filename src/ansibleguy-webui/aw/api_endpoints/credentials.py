from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from aw.model.job import Job, JobExecution
from aw.model.job_credential import BaseJobCredentials, JobUserCredentials, JobGlobalCredentials
from aw.model.permission import CHOICE_PERMISSION_READ, CHOICE_PERMISSION_WRITE, CHOICE_PERMISSION_DELETE
from aw.api_endpoints.base import API_PERMISSION, get_api_user, GenericResponse, BaseResponse
from aw.utils.permission import has_credentials_permission, has_manager_privileges
from aw.utils.util import is_null
from aw.base import USERS


class JobGlobalCredentialsReadResponse(serializers.ModelSerializer):
    class Meta:
        model = JobGlobalCredentials
        fields = JobGlobalCredentials.api_fields_read

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for secret_attr in BaseJobCredentials.SECRET_ATTRS:
            setattr(self, f'{secret_attr}_is_set', serializers.BooleanField(required=False))


class JobUserCredentialsReadResponse(JobGlobalCredentialsReadResponse):
    class Meta:
        model = JobUserCredentials
        fields = JobUserCredentials.api_fields_read


class JobCredentialsList(BaseResponse):
    # NOTE: 'global' attribute not usable..
    shared = serializers.ListSerializer(child=JobGlobalCredentialsReadResponse())
    user = serializers.ListSerializer(child=JobUserCredentialsReadResponse())


class JobGlobalCredentialsWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = JobGlobalCredentials
        fields = JobGlobalCredentials.api_fields_write

    vault_pass = serializers.CharField(max_length=100, required=False, default=None, allow_blank=True)
    become_pass = serializers.CharField(max_length=100, required=False, default=None, allow_blank=True)
    connect_pass = serializers.CharField(max_length=100, required=False, default=None, allow_blank=True)
    ssh_key = serializers.CharField(max_length=2000, required=False, default=None, allow_blank=True)


class JobUserCredentialsWriteRequest(JobGlobalCredentialsWriteRequest):
    class Meta:
        model = JobUserCredentials
        fields = JobUserCredentials.api_fields_write


def are_global_credentials(request) -> bool:
    if 'global' in request.GET and request.GET['global'] != 'true':
        return False

    return True


def _find_credentials(
        credentials_id: int, are_global: bool, user: USERS
) -> (BaseJobCredentials, None):
    try:
        if are_global:
            return JobGlobalCredentials.objects.get(id=credentials_id)

        return JobUserCredentials.objects.get(id=credentials_id, user=user)

    except ObjectDoesNotExist:
        return None


def _log_global_user(are_global: bool, lower: bool = False) -> str:
    if are_global:
        msg = 'Global credentials'

    else:
        msg = 'User credentials'

    if lower:
        return msg.lower()

    return msg


def credentials_in_use(credentials: BaseJobCredentials) -> bool:
    if isinstance(credentials, JobGlobalCredentials):
        in_use_jobs = Job.objects.filter(credentials_default=credentials).exists()
        in_use_execs = JobExecution.objects.filter(credential_global=credentials).exists()
        in_use = in_use_jobs or in_use_execs

    else:
        in_use = JobExecution.objects.filter(credential_user=credentials).exists()

    return in_use


SSH_KEY_PREFIX = '-----BEGIN OPENSSH PRIVATE KEY-----'
SSH_KEY_APPENDIX = '-----END OPENSSH PRIVATE KEY-----'


def _validate_and_fix_ssh_key(key: str) -> (str, None):
    if key.find(SSH_KEY_PREFIX) == -1:
        # only support unencrypted keys for now
        return None

    key = key.replace(SSH_KEY_PREFIX, '').replace(SSH_KEY_APPENDIX, '').strip().replace(' ', '\n')
    return f'{SSH_KEY_PREFIX}\n{key}\n{SSH_KEY_APPENDIX}\n'


class APIJobCredentials(APIView):
    http_method_names = ['get', 'post']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION
    parameters = [
        OpenApiParameter(
            name='global', type=bool, default=True,
            description='If the credentials are global or user-specific',
            required=False,
        ),
    ]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobCredentialsList, description='Return list of credentials'),
        },
        summary='Return list of all credentials the current user is privileged to view.',
        operation_id='credentials_list',
    )
    def get(self, request):
        user = get_api_user(request)
        credentials_global = []
        credentials_global_raw = JobGlobalCredentials.objects.all()
        for credentials in credentials_global_raw:
            if has_credentials_permission(
                    user=user,
                    credentials=credentials,
                    permission_needed=CHOICE_PERMISSION_READ,
            ):
                credentials_global.append(JobGlobalCredentialsReadResponse(instance=credentials).data)

        credentials_user_raw = JobUserCredentials.objects.filter(user=user)
        credentials_user = []
        for credentials in credentials_user_raw:
            credentials_user.append(JobUserCredentialsReadResponse(instance=credentials).data)

        return Response(data={'shared': credentials_global, 'user': credentials_user}, status=200)

    @extend_schema(
        request=JobGlobalCredentialsWriteRequest,
        responses={
            200: OpenApiResponse(GenericResponse, description='Credentials created'),
            400: OpenApiResponse(GenericResponse, description='Invalid credentials data provided'),
            403: OpenApiResponse(GenericResponse, description='Not privileged to create global credentials'),
        },
        summary='Create credentials.',
        operation_id='credentials_create',
        parameters=parameters,
    )
    def post(self, request):
        user = get_api_user(request)
        are_global = are_global_credentials(request)

        if are_global and not has_manager_privileges(user=user, kind='credentials'):
            return Response(data={'msg': 'Not privileged to create global credentials'}, status=403)

        if are_global:
            self.serializer_class = JobGlobalCredentialsWriteRequest

        else:
            self.serializer_class = JobUserCredentialsWriteRequest

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided {_log_global_user(are_global)} data is not valid: '{serializer.errors}'"},
                status=400,
            )

        for field in BaseJobCredentials.SECRET_ATTRS:
            value = serializer.validated_data[field]
            if field in BaseJobCredentials.SECRET_ATTRS:
                if is_null(value) or value == BaseJobCredentials.SECRET_HIDDEN:
                    serializer.validated_data[field] = None

                elif field == 'ssh_key':
                    value = _validate_and_fix_ssh_key(value)
                    if value is None:
                        return Response(
                            data={'msg': f"Provided {_log_global_user(are_global)} ssh-key is not valid'"},
                            status=400,
                        )

                    serializer.validated_data[field] = value

        try:
            serializer.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided {_log_global_user(are_global)} data is not valid: '{err}'"},
                status=400,
            )

        return Response(data={'msg': f'{_log_global_user(are_global, lower=False)} created'}, status=200)


class APIJobCredentialsItem(APIView):
    http_method_names = ['get', 'delete', 'put']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION
    parameters = [
        OpenApiParameter(
            name='global', type=bool, default=True,
            description='If the credentials are global or user-specific',
            required=False,
        ),
    ]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobUserCredentialsReadResponse, description='Return information about credentials'),
            403: OpenApiResponse(GenericResponse, description='Not privileged to view the credentials'),
            404: OpenApiResponse(GenericResponse, description='Credentials not exist'),
        },
        summary='Return information about a set of credentials.',
        operation_id='credentials_view',
        parameters=parameters,
    )
    def get(self, request, credentials_id: int):
        user = get_api_user(request)
        are_global = are_global_credentials(request)

        if are_global:
            self.serializer_class = JobGlobalCredentialsReadResponse

        else:
            self.serializer_class = JobUserCredentialsReadResponse

        credentials = _find_credentials(
            credentials_id=credentials_id,
            are_global=are_global,
            user=user,
        )
        if credentials is None:
            base_msg = f"{_log_global_user(are_global)} with ID {credentials_id} do not exist"
            if not are_global:
                return Response(data={'msg': f"{base_msg} or belong to another user"}, status=404)

            return Response(data={'msg': base_msg}, status=404)

        if are_global and not has_credentials_permission(
                user=user,
                credentials=credentials,
                permission_needed=CHOICE_PERMISSION_READ,
        ):
            return Response(
                data={'msg': f"{_log_global_user(are_global)} '{credentials.name}' are not viewable"},
                status=403,
            )

        return Response(data=self.serializer_class(instance=credentials).data, status=200)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(GenericResponse, description='Credentials deleted'),
            403: OpenApiResponse(GenericResponse, description='Not privileged to delete the credentials'),
            404: OpenApiResponse(GenericResponse, description='Credentials do not exist'),
        },
        summary='Delete credentials.',
        operation_id='credentials_delete',
        parameters=parameters,
    )
    def delete(self, request, credentials_id: int):
        user = get_api_user(request)
        are_global = are_global_credentials(request)

        if are_global:
            self.serializer_class = JobGlobalCredentialsReadResponse

        else:
            self.serializer_class = JobUserCredentialsReadResponse

        credentials = _find_credentials(
            credentials_id=credentials_id,
            are_global=are_global,
            user=user,
        )
        if credentials is None:
            base_msg = f"{_log_global_user(are_global)} with ID {credentials_id} do not exist"
            if not are_global:
                return Response(data={'msg': f"{base_msg} or belong to another user"}, status=404)

            return Response(data={'msg': base_msg}, status=404)

        if are_global and not has_credentials_permission(
                user=user,
                credentials=credentials,
                permission_needed=CHOICE_PERMISSION_DELETE,
        ):
            return Response(
                data={'msg': f"Not privileged to delete the {_log_global_user(are_global, lower=True)} "
                             f"'{credentials.name}'"},
                status=403)

        if credentials_in_use(credentials):
            return Response(
                data={'msg': f"{_log_global_user(are_global)} '{credentials.name}' cannot be deleted "
                             "as they are still in use"},
                status=400,
            )

        credentials.delete()
        return Response(data={'msg': f"{_log_global_user(are_global)} '{credentials.name}' deleted"}, status=200)

    @extend_schema(
        request=JobGlobalCredentialsWriteRequest,
        responses={
            200: OpenApiResponse(GenericResponse, description='Credentials updated'),
            400: OpenApiResponse(GenericResponse, description='Invalid credentials data provided'),
            403: OpenApiResponse(GenericResponse, description='Not privileged to modify the credentials'),
            404: OpenApiResponse(GenericResponse, description='Credentials do not exist'),
        },
        summary='Modify credentials.',
        operation_id='credentials_edit',
        parameters=parameters,
    )
    def put(self, request, credentials_id: int):
        user = get_api_user(request)
        are_global = are_global_credentials(request)

        if are_global:
            self.serializer_class = JobGlobalCredentialsWriteRequest

        else:
            self.serializer_class = JobUserCredentialsWriteRequest

        credentials = _find_credentials(
            credentials_id=credentials_id,
            are_global=are_global,
            user=user,
        )
        if credentials is None:
            base_msg = f"{_log_global_user(are_global)} with ID {credentials_id} do not exist"
            if not are_global:
                return Response(data={'msg': f"{base_msg} or belong to another user"}, status=404)

            return Response(data={'msg': base_msg}, status=404)

        if are_global and not has_credentials_permission(
                user=user,
                credentials=credentials,
                permission_needed=CHOICE_PERMISSION_WRITE,
        ):
            return Response(
                data={'msg': f"Not privileged to modify the {_log_global_user(are_global, lower=True)} "
                             f"'{credentials.name}'"},
                status=403,
            )

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided {_log_global_user(are_global, lower=True)} data is not valid: "
                             f"'{serializer.errors}'"},
                status=400,
            )

        try:
            # not working with password properties: 'Job.objects.filter(id=job_id).update(**serializer.data)'
            for field, value in serializer.data.items():
                if field in BaseJobCredentials.SECRET_ATTRS:
                    if is_null(value) or value == BaseJobCredentials.SECRET_HIDDEN:
                        value = getattr(credentials, field)

                    elif field == 'ssh_key':
                        value = _validate_and_fix_ssh_key(value)
                        if value is None:
                            return Response(
                                data={'msg': f"Provided {_log_global_user(are_global)} ssh-key is not valid'"},
                                status=400,
                            )

                elif field == 'user':
                    continue

                setattr(credentials, field, value)

            if not are_global:
                credentials.user = user

            credentials.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided {_log_global_user(are_global, lower=True)} data is not valid: '{err}'"},
                status=400,
            )

        return Response(data={'msg': f"{_log_global_user(are_global)} '{credentials.name}' updated"}, status=200)
