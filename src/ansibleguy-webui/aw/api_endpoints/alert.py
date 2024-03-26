from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.api_endpoints.base import API_PERMISSION, GenericResponse, get_api_user, api_docs_put, api_docs_delete, \
    api_docs_post
from aw.utils.permission import has_manager_privileges
from aw.model.alert import AlertPlugin, AlertGlobal, AlertGroup, AlertUser


class AlertPluginReadWrite(serializers.ModelSerializer):
    class Meta:
        model = AlertPlugin
        fields = AlertPlugin.api_fields


class APIAlertPlugin(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertPluginReadWrite
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertPluginReadWrite},
        summary='Return list of Alert-Plugins',
        operation_id='alert_plugin_list',
    )
    def get(request):
        del request
        return Response([AlertPluginReadWrite(instance=plugin).data for plugin in AlertPlugin.objects.all()])

    @extend_schema(
        request=AlertPluginReadWrite,
        responses=api_docs_post('Alert-Plugin'),
        summary='Create a new Alert-Plugin.',
        operation_id='alert_plugin_create',
    )
    def post(self, request):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alert-Plugin'},
                status=403,
            )

        serializer = AlertPluginReadWrite(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert-Plugin data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            serializer.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided Alert-Plugin data is not valid: '{err}'"},
                status=400,
            )

        return Response({'msg': f"Alert-Plugin '{serializer.validated_data['name']}' created successfully"})


class APIAlertPluginItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertPluginReadWrite,
            404: OpenApiResponse(response=GenericResponse, description='Alert-Plugin does not exist'),
        },
        summary='Return information of an Alert-Plugin.',
        operation_id='alert_plugin_get'
    )
    def get(request, plugin_id: int):
        del request
        try:
            plugin = AlertPlugin.objects.get(id=plugin_id)
            if plugin is not None:
                return Response(AlertPluginReadWrite(instance=plugin).data)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Alert-Plugin with ID {plugin_id} does not exist"}, status=404)

    @extend_schema(
        request=AlertPluginReadWrite,
        responses=api_docs_put('Alert-Plugin'),
        summary='Modify an Alert-Plugin.',
        operation_id='alert_plugin_edit',
    )
    def put(self, request, plugin_id: int):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alert-Plugins'},
                status=403,
            )

        serializer = AlertPluginReadWrite(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert-Plugin data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            plugin = AlertPlugin.objects.get(id=plugin_id)

        except ObjectDoesNotExist:
            plugin = None

        if plugin is None:
            return Response(
                data={'msg': f"Alert-Plugin with ID {plugin_id} does not exist"},
                status=404,
            )

        try:
            AlertPlugin.objects.filter(id=plugin.id).update(**serializer.validated_data)
            return Response(data={'msg': f"Alert-Plugin '{plugin.name}' updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'msg': f"Provided Alert-Plugin data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert-Plugin'),
        summary='Delete an Alert-Plugin.',
        operation_id='alert_plugin_delete'
    )
    def delete(self, request, plugin_id: int):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alert-Plugins'},
                status=403,
            )

        try:
            plugin = AlertPlugin.objects.get(id=plugin_id)
            if plugin is not None:
                plugin.delete()
                return Response(data={'msg': f"Alert-Plugin '{plugin.name}' deleted"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Alert-Plugin with ID {plugin_id} does not exist"}, status=404)


class AlertUserReadResponse(serializers.ModelSerializer):
    class Meta:
        model = AlertUser
        fields = AlertUser.api_fields_read

    alert_type_name = serializers.CharField()
    condition_name = serializers.CharField()


class AlertUserWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = AlertUser
        fields = AlertUser.api_fields_write


class APIAlertUser(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertUserReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertUserReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_user_list',
    )
    def get(request):
        user = get_api_user(request)
        return Response(
            [AlertUserReadResponse(instance=alert).data for alert in AlertUser.objects.filter(user=user)]
        )

    @extend_schema(
        request=AlertUserWriteRequest,
        responses=api_docs_post('Alert'),
        summary='Create a new Alert.',
        operation_id='alert_user_create',
    )
    def post(self, request):
        user = get_api_user(request)
        serializer = AlertUserWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            serializer.validated_data['user_id'] = user.id
            serializer.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{err}'"},
                status=400,
            )

        return Response({'msg': f"Alert '{serializer.validated_data['name']}' created successfully"})


class APIAlertUserItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertUserReadResponse,
            404: OpenApiResponse(response=GenericResponse, description='Alert does not exist'),
        },
        summary='Return information of an Alert.',
        operation_id='alert_user_get'
    )
    def get(request, alert_id: int):
        user = get_api_user(request)

        try:
            alert = AlertUser.objects.get(id=alert_id, user=user)
            if alert is not None:
                return Response(AlertUserReadResponse(instance=alert).data)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'msg': f"Alert with ID {alert_id} does not exist or is belongs to another user"},
            status=404,
        )

    @extend_schema(
        request=AlertUserWriteRequest,
        responses=api_docs_put('Alert'),
        summary='Modify an Alert.',
        operation_id='alert_user_edit',
    )
    def put(self, request, alert_id: int):
        user = get_api_user(request)
        serializer = AlertUserWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            alert = AlertUser.objects.get(id=alert_id, user=user)

        except ObjectDoesNotExist:
            alert = None

        if alert is None:
            return Response(
                data={'msg': f"Alert with ID {alert_id} does not exist or is belongs to another user"},
                status=404,
            )

        try:
            AlertUser.objects.filter(id=alert.id).update(
                **{**serializer.validated_data, 'user': user.id}
            )
            return Response(data={'msg': f"Alert '{alert.name}' updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'msg': f"Provided Alert data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert'),
        summary='Delete an Alert.',
        operation_id='alert_user_delete'
    )
    def delete(self, request, alert_id: int):
        user = get_api_user(request)

        try:
            alert = AlertUser.objects.get(id=alert_id, user=user)
            if alert is not None:
                alert.delete()
                return Response(data={'msg': f"Alert '{alert.name}' deleted"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'msg': f"Alert with ID {alert_id} does not exist or is belongs to another user"},
            status=404,
        )


class AlertGlobalReadResponse(serializers.ModelSerializer):
    class Meta:
        model = AlertGlobal
        fields = AlertGlobal.api_fields_read

    alert_type_name = serializers.CharField()
    condition_name = serializers.CharField()


class AlertGlobalWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = AlertGlobal
        fields = AlertGlobal.api_fields_write


class APIAlertGlobal(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertGlobalReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertGlobalReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_global_list',
    )
    def get(request):
        del request
        return Response([AlertGlobalReadResponse(instance=alert).data for alert in AlertGlobal.objects.all()])

    @extend_schema(
        request=AlertGlobalReadResponse,
        responses=api_docs_post('Alert'),
        summary='Create a new Alert.',
        operation_id='alert_global_create',
    )
    def post(self, request):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alert'},
                status=403,
            )

        serializer = AlertGlobalWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            serializer.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{err}'"},
                status=400,
            )

        return Response({'msg': f"Alert '{serializer.validated_data['name']}' created successfully"})


class APIAlertGlobalItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertGlobalReadResponse,
            404: OpenApiResponse(response=GenericResponse, description='Alert does not exist'),
        },
        summary='Return information of an Alert.',
        operation_id='alert_global_get'
    )
    def get(request, alert_id: int):
        del request
        try:
            alert = AlertGlobal.objects.get(id=alert_id)
            if alert is not None:
                return Response(AlertGlobalReadResponse(instance=alert).data)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Alert with ID {alert_id} does not exist"}, status=404)

    @extend_schema(
        request=AlertGlobalWriteRequest,
        responses=api_docs_put('Alert'),
        summary='Modify an Alert.',
        operation_id='alert_global_edit',
    )
    def put(self, request, alert_id: int):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alerts'},
                status=403,
            )

        serializer = AlertGlobalWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            alert = AlertGlobal.objects.get(id=alert_id)

        except ObjectDoesNotExist:
            alert = None

        if alert is None:
            return Response(
                data={'msg': f"Alert with ID {alert_id} does not exist"},
                status=404,
            )

        try:
            AlertGlobal.objects.filter(id=alert.id).update(**serializer.validated_data)
            return Response(data={'msg': f"Alert '{alert.name}' updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'msg': f"Provided Alert data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert'),
        summary='Delete an Alert.',
        operation_id='alert_global_delete'
    )
    def delete(self, request, alert_id: int):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alerts'},
                status=403,
            )

        try:
            alert = AlertGlobal.objects.get(id=alert_id)
            if alert is not None:
                alert.delete()
                return Response(data={'msg': f"Alert '{alert.name}' deleted"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Alert with ID {alert_id} does not exist"}, status=404)


class AlertGroupReadResponse(serializers.ModelSerializer):
    class Meta:
        model = AlertGroup
        fields = AlertGroup.api_fields_read

    alert_type_name = serializers.CharField()
    condition_name = serializers.CharField()
    group_name = serializers.CharField()


class AlertGroupWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = AlertGroup
        fields = AlertGroup.api_fields_write


class APIAlertGroup(GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = AlertGroupReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: AlertGroupReadResponse},
        summary='Return list of Alerts',
        operation_id='alert_group_list',
    )
    def get(request):
        del request
        return Response(
            [AlertGroupReadResponse(instance=alert).data for alert in AlertGroup.objects.filter()]
        )

    @extend_schema(
        request=AlertGroupWriteRequest,
        responses=api_docs_post('Alert'),
        summary='Create a new Alert.',
        operation_id='alert_group_create',
    )
    def post(self, request):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alerts'},
                status=403,
            )

        serializer = AlertGroupWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            serializer.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{err}'"},
                status=400,
            )

        return Response({'msg': f"Alert '{serializer.validated_data['name']}' created successfully"})


class APIAlertGroupItem(GenericAPIView):
    http_method_names = ['get', 'put', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: AlertGroupReadResponse,
            404: OpenApiResponse(response=GenericResponse, description='Alert does not exist'),
        },
        summary='Return information of an Alert.',
        operation_id='alert_group_get'
    )
    def get(request, alert_id: int):
        del request

        try:
            alert = AlertGroup.objects.get(id=alert_id)
            if alert is not None:
                return Response(AlertGroupReadResponse(instance=alert).data)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'msg': f"Alert with ID {alert_id} does not exist"},
            status=404,
        )

    @extend_schema(
        request=AlertGroupWriteRequest,
        responses=api_docs_put('Alert'),
        summary='Modify an Alert.',
        operation_id='alert_group_edit',
    )
    def put(self, request, alert_id: int):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alerts'},
                status=403,
            )

        serializer = AlertGroupWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided Alert data is not valid: '{serializer.errors}'"},
                status=400,
            )

        try:
            alert = AlertGroup.objects.get(id=alert_id)

        except ObjectDoesNotExist:
            alert = None

        if alert is None:
            return Response(
                data={'msg': f"Alert with ID {alert_id} does not exist"},
                status=404,
            )

        try:
            AlertGroup.objects.filter(id=alert.id).update(**serializer.validated_data)
            return Response(data={'msg': f"Alert '{alert.name}' updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'msg': f"Provided Alert data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Alert'),
        summary='Delete an Alert.',
        operation_id='alert_group_delete'
    )
    def delete(self, request, alert_id: int):
        privileged = has_manager_privileges(user=get_api_user(request), kind='alert')
        if not privileged:
            return Response(
                data={'msg': 'Not privileged to manage Alerts'},
                status=403,
            )

        try:
            alert = AlertGroup.objects.get(id=alert_id)
            if alert is not None:
                alert.delete()
                return Response(data={'msg': f"Alert '{alert.name}' deleted"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(
            data={'msg': f"Alert with ID {alert_id} does not exist"},
            status=404,
        )
