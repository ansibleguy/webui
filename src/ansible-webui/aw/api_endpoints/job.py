from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.models import Job
from aw.api_endpoints.base import API_PERMISSION, get_api_user, BaseResponse
from aw.api_endpoints.job_util import get_viewable_jobs_serialized, get_job_if_allowed, \
    JobReadResponse
from aw.model.job import CHOICE_JOB_PERMISSION_READ, CHOICE_JOB_PERMISSION_WRITE


class JobWriteRequest(JobReadResponse):
    pass


class JobWriteResponse(BaseResponse):
    msg = serializers.CharField()


class JobListCreate(APIView):
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


class JobViewEditDelete(APIView):
    http_method_names = ['get', 'delete', 'put']
    serializer_class = JobWriteResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobReadResponse, description='Return job information'),
            404: OpenApiResponse(JobReadResponse, description='Job does not exist'),
        },
        summary='Return information about an existing job.',
    )
    def get(request, job_id: int):
        # pylint: disable=E1101
        user = get_api_user(request)
        job = get_job_if_allowed(
            user=user,
            job=Job.objects.filter(id=job_id),
            permission_needed=CHOICE_JOB_PERMISSION_READ,
        )
        if job is None:
            return Response(data={'msg': 'Job does not exist or is not viewable'}, status=404)

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
        # pylint: disable=E1101
        user = get_api_user(request)
        try:
            result = Job.objects.filter(id=job_id)

            if result.exists():
                result = get_job_if_allowed(user=user, job=result, permission_needed=CHOICE_JOB_PERMISSION_WRITE)

                if result is not None:
                    result.delete()
                    return Response(data={'msg': 'Job deleted'}, status=200)

                return Response(data={'msg': 'Not privileged to delete the job'}, status=403)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': 'Job does not exist'}, status=404)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobWriteResponse, description='Job updated'),
            400: OpenApiResponse(JobWriteResponse, description='Invalid job data provided'),
            403: OpenApiResponse(JobWriteResponse, description='Not privileged to modify the job'),
            404: OpenApiResponse(JobWriteResponse, description='Job does not exist'),
        },
        summary='Delete an existing job.',
    )
    def put(self, request, job_id: int):
        # pylint: disable=E1101
        user = get_api_user(request)
        try:
            result = Job.objects.filter(id=job_id)

            if result.exists():
                result = get_job_if_allowed(user=user, job=result, permission_needed=CHOICE_JOB_PERMISSION_WRITE)

                if result is None:
                    return Response(data={'msg': 'Not privileged to modify the job'}, status=403)

                serializer = JobWriteRequest(data=request.data)
                if not serializer.is_valid():
                    return Response(data={'msg': 'Provided job data is not valid'}, status=400)

                result.update(**serializer.data)
                result.save()
                return Response(data={'msg': 'Job updated'}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'msg': 'Job does not exist'}, status=404)
