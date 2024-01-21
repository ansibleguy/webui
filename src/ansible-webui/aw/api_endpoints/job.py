from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.models import Job
from aw.api_endpoints.base import API_PERMISSION, get_api_user, BaseResponse
from aw.api_endpoints.job_util import get_viewable_jobs_serialized, job_action_allowed, \
    JobReadResponse
from aw.model.job import CHOICE_JOB_PERMISSION_READ, CHOICE_JOB_PERMISSION_WRITE, CHOICE_JOB_PERMISSION_EXECUTE


class JobWriteRequest(JobReadResponse):
    pass


class JobWriteResponse(BaseResponse):
    msg = serializers.CharField()


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
    )
    def post(self, request):
        serializer = JobWriteRequest(data=request.data)
        if not serializer.is_valid():
            return Response(data={'msg': 'Provided job data is not valid'}, status=400)

        serializer.save()
        return Response(data={'msg': 'Job created'}, status=200)


class APIJobItem(APIView):
    http_method_names = ['get', 'delete', 'put', 'post']
    serializer_class = JobWriteResponse
    permission_classes = API_PERMISSION

    @staticmethod
    def _find_job(job_id: int) -> (Job, None):
        # pylint: disable=E1101
        return Job.objects.get(id=job_id)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Return job information'),
            404: OpenApiResponse(JobReadResponse, description='Job does not exist'),
        },
        summary='Return information about an existing job.',
    )
    def get(self, request, job_id: int):
        self.serializer_class = JobReadResponse
        user = get_api_user(request)
        job = self._find_job(job_id)
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
    )
    def delete(self, request, job_id: int):
        user = get_api_user(request)
        try:
            job = self._find_job(job_id)

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
    )
    def put(self, request, job_id: int):
        user = get_api_user(request)
        try:
            job = self._find_job(job_id)

            if job is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_WRITE):
                    return Response(data={'msg': f"Not privileged to modify the job '{job.name}'"}, status=403)

                serializer = JobWriteRequest(data=request.data)
                if not serializer.is_valid():
                    return Response(data={'msg': 'Provided job data is not valid'}, status=400)

                # pylint: disable=E1101
                Job.objects.filter(id=job_id).update(**serializer.data)
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
        summary='Execute an existing job.',
    )
    def post(self, request, job_id: int):
        user = get_api_user(request)
        try:
            job = self._find_job(job_id)

            if job is not None:
                if not job_action_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_EXECUTE):
                    return Response(data={'msg': f"Not privileged to execute the job '{job.name}'"}, status=403)

                # todo: queue job for execution
                return Response(data={'msg': f"Job '{job.name}' execution queued"}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': f"Job with ID '{job_id}' does not exist"}, status=404)
