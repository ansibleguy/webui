from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.model.job import Job, JobExecution, BaseJobCredentials, \
    CHOICE_JOB_PERMISSION_READ, CHOICE_JOB_PERMISSION_WRITE, CHOICE_JOB_PERMISSION_EXECUTE
from aw.api_endpoints.base import API_PERMISSION, get_api_user, BaseResponse
from aw.api_endpoints.job_util import get_viewable_jobs_serialized, job_action_allowed, \
    JobReadResponse
from aw.execute.queue import queue_add
from aw.execute.util import update_execution_status, is_execution_status
from aw.utils.util import is_null

LIMIT_JOB_RESULTS = 10


class JobWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = Job.api_fields_write

    vault_pass = serializers.CharField(max_length=100, required=False, default=None)
    become_pass = serializers.CharField(max_length=100, required=False, default=None)
    connect_pass = serializers.CharField(max_length=100, required=False, default=None)


class JobWriteResponse(BaseResponse):
    msg = serializers.CharField()


def _find_job(job_id: int) -> (Job, None):
    # pylint: disable=E1101
    return Job.objects.get(id=job_id)


def _find_job_and_execution(job_id: int, exec_id: int) -> tuple[Job, JobExecution]:
    # pylint: disable=E1101
    job = _find_job(job_id)
    return job, JobExecution.objects.get(id=exec_id, job=job)


class APIJob(APIView):
    http_method_names = ['post', 'get']
    serializer_class = JobReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Return list of jobs'),
        },
        summary='Return list of all jobs the current user is privileged to view.',
        operation_id='job_list'
    )
    def get(request):
        return Response(data=get_viewable_jobs_serialized(get_api_user(request)), status=200)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobWriteResponse, description='Job created'),
            400: OpenApiResponse(JobWriteResponse, description='Invalid job data provided'),
        },
        summary='Create a new job.',
        operation_id='job_create'
    )
    def post(self, request):
        serializer = JobWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'msg': f"Provided job data is not valid: '{serializer.errors}'"},
                status=400,
            )

        for field in BaseJobCredentials.PWD_ATTRS:
            value = serializer.validated_data[field]
            if field in BaseJobCredentials.PWD_ATTRS and \
                    (is_null(value) or value == BaseJobCredentials.PWD_HIDDEN):
                serializer.validated_data[field] = None

        try:
            serializer.save()

        except IntegrityError as err:
            return Response(
                data={'msg': f"Provided job data is not valid: '{err}'"},
                status=400,
            )

        return Response(data={'msg': 'Job created'}, status=200)


class APIJobItem(APIView):
    http_method_names = ['get', 'delete', 'put', 'post']
    serializer_class = JobWriteResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Return job information'),
            404: OpenApiResponse(JobReadResponse, description='Job does not exist'),
        },
        summary='Return information about an existing job.',
        operation_id='job_view'
    )
    def get(self, request, job_id: int):
        self.serializer_class = JobReadResponse
        user = get_api_user(request)
        job = _find_job(job_id)
        if job is None:
            return Response(data={'msg': f"Job with ID {job_id} does not exist"}, status=404)

        if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_READ):
            return Response(data={'msg': f"Job '{job.name}' is not viewable"}, status=403)

        return Response(data=JobReadResponse(instance=job).data, status=200)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobWriteResponse, description='Job deleted'),
            403: OpenApiResponse(JobWriteResponse, description='Not privileged to delete the job'),
            404: OpenApiResponse(JobWriteResponse, description='Job does not exist'),
        },
        summary='Delete an existing job.',
        operation_id='job_delete'
    )
    def delete(self, request, job_id: int):
        user = get_api_user(request)
        try:
            job = _find_job(job_id)

            if job is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_WRITE):
                    return Response(data={'msg': f"Not privileged to delete the job '{job.name}'"}, status=403)

                job.delete()
                return Response(data={'msg': f"Job '{job.name}' deleted"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Job with ID {job_id} does not exist"}, status=404)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobWriteResponse, description='Job updated'),
            400: OpenApiResponse(JobWriteResponse, description='Invalid job data provided'),
            403: OpenApiResponse(JobWriteResponse, description='Not privileged to modify the job'),
            404: OpenApiResponse(JobWriteResponse, description='Job does not exist'),
        },
        summary='Modify an existing job.',
        operation_id='job_edit'
    )
    def put(self, request, job_id: int):
        user = get_api_user(request)
        try:
            job = _find_job(job_id)

            if job is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_WRITE):
                    return Response(data={'msg': f"Not privileged to modify the job '{job.name}'"}, status=403)

                serializer = JobWriteRequest(data=request.data)
                if not serializer.is_valid():
                    return Response(
                        data={'msg': f"Provided job data is not valid: '{serializer.errors}'"},
                        status=400,
                    )

                # pylint: disable=E1101
                try:
                    # not working with password properties: 'Job.objects.filter(id=job_id).update(**serializer.data)'
                    for field, value in serializer.data.items():
                        if field in BaseJobCredentials.PWD_ATTRS and \
                                (is_null(value) or value == BaseJobCredentials.PWD_HIDDEN):
                            value = getattr(job, field)

                        setattr(job, field, value)

                    job.save()

                except IntegrityError as err:
                    return Response(
                        data={'msg': f"Provided job data is not valid: '{err}'"},
                        status=400,
                    )

                return Response(data={'msg': f"Job '{job.name}' updated"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Job with ID {job_id} does not exist"}, status=404)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Job execution queued'),
            403: OpenApiResponse(JobReadResponse, description='Not privileged to execute the job'),
            404: OpenApiResponse(JobReadResponse, description='Job does not exist'),
        },
        summary='Execute a job.',
        operation_id='job_execute'
    )
    def post(self, request, job_id: int):
        user = get_api_user(request)
        try:
            job = _find_job(job_id)

            if job is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_EXECUTE):
                    return Response(data={'msg': f"Not privileged to execute the job '{job.name}'"}, status=403)

                queue_add(job=job, user=user)
                return Response(data={'msg': f"Job '{job.name}' execution queued"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Job with ID '{job_id}' does not exist"}, status=404)


class APIJobExecutionItem(APIView):
    http_method_names = ['delete']
    serializer_class = JobWriteResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Job execution stopping'),
            400: OpenApiResponse(JobReadResponse, description='Job execution is not running'),
            403: OpenApiResponse(JobReadResponse, description='Not privileged to stop the job'),
            404: OpenApiResponse(JobReadResponse, description='Job or execution does not exist'),
        },
        summary='Stop a running job execution.',
        operation_id='job_exec_stop'
    )
    def delete(self, request, job_id: int, exec_id: int):
        user = get_api_user(request)
        try:
            job, execution = _find_job_and_execution(job_id, exec_id)

            if job is not None and execution is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_EXECUTE):
                    return Response(data={'msg': f"Not privileged to stop the job '{job.name}'"}, status=403)

                if not is_execution_status(execution, 'Running'):
                    return Response(data={'msg': f"Job execution '{job.name}' is not running"}, status=400)

                update_execution_status(execution, 'Stopping')
                return Response(data={'msg': f"Job execution '{job.name}' stopping"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Job with ID '{job_id}' or execution does not exist"}, status=404)


class JobExecutionLogReadResponse(BaseResponse):
    lines = serializers.ListSerializer(child=serializers.CharField())


class APIJobExecutionLogs(APIView):
    http_method_names = ['get']
    serializer_class = JobExecutionLogReadResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Return job logs'),
            403: OpenApiResponse(JobReadResponse, description='Not privileged to view the job logs'),
            404: OpenApiResponse(JobReadResponse, description='Job, execution or logs do not exist'),
        },
        summary='Get logs of a job execution.',
        operation_id='job_exec_logs'
    )
    def get(self, request, job_id: int, exec_id: int, line_start: int = 0):
        user = get_api_user(request)
        try:
            job, execution = _find_job_and_execution(job_id, exec_id)

            if job is not None and execution is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_READ):
                    return Response(data={'msg': f"Not privileged to view logs of the job '{job.name}'"}, status=403)

                if execution.log_stdout is None:
                    return Response(data={'msg': f"No logs found for job '{job.name}'"}, status=404)

                with open(execution.log_stdout, 'r', encoding='utf-8') as logfile:
                    lines = logfile.readlines()
                    return Response(data={'lines': lines[line_start:]}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Job with ID '{job_id}' or execution does not exist"}, status=404)
