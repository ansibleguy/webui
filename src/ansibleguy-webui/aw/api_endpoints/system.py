from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db.utils import IntegrityError

from aw.config.main import config
from aw.model.system import SystemConfig, get_config_from_db
from aw.api_endpoints.base import API_PERMISSION, get_api_user, GenericResponse, BaseResponse
from aw.utils.util_no_config import is_set
from aw.utils.debug import log
from aw.utils.permission import has_manager_privileges


class SystemConfigReadResponse(BaseResponse):
    # todo: fix static fields.. duplicate logic in model

    # SystemConfig.form_fields
    path_run = serializers.CharField()
    path_play = serializers.CharField()
    path_log = serializers.CharField()
    timezone = serializers.CharField()
    run_timeout = serializers.IntegerField()
    session_timeout = serializers.IntegerField()
    path_ansible_config = serializers.CharField()
    path_ssh_known_hosts = serializers.CharField()

    # SystemConfig.api_fields_read_only
    db = serializers.CharField()
    db_migrate = serializers.BooleanField()
    serve_static = serializers.BooleanField()
    deployment = serializers.CharField()
    version = serializers.CharField()
    logo_url = serializers.CharField()
    ara_server = serializers.CharField()
    global_environment_vars = serializers.CharField()


class SystemConfigWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = SystemConfig.api_fields_write


class APISystemConfig(APIView):
    http_method_names = ['put', 'get']
    serializer_class = SystemConfigReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: SystemConfigReadResponse},
        summary='Return currently active config.',
        operation_id='system_config_view',
    )
    def get(request):
        del request
        merged_config = {'read_only_settings': SystemConfig.api_fields_read_only}

        for field in SystemConfig.form_fields + merged_config['read_only_settings']:
            merged_config[field] = config[field]

        merged_config['read_only_settings'] += SystemConfig.get_set_env_vars()

        return Response(merged_config)

    @extend_schema(
        request=SystemConfigWriteRequest,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='System config updated'),
            400: OpenApiResponse(response=GenericResponse, description='Invalid system config provided'),
            403: OpenApiResponse(response=GenericResponse, description='Not privileged to update the system config'),
        },
        summary='Modify system config.',
        operation_id='system_config_edit',
    )
    def put(self, request):
        privileged = has_manager_privileges(user=get_api_user(request), kind='system')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage system config'},
                status=403,
            )

        serializer = SystemConfigWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided system config is not valid: '{serializer.errors}'"},
                status=400,
            )

        config_db = get_config_from_db()
        try:
            changed = False
            for setting, value in serializer.validated_data.items():
                if is_set(value) and str(config[setting]) != str(value):
                    setattr(config_db, setting, value)
                    changed = True

            if changed:
                log(msg='System config change - updating', level=5)
                config_db.save()

            return Response(data={'msg': "System config updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'msg': f"Provided system config is not valid: '{err}'"}, status=400)
