from django.contrib import admin
from rest_framework_api_key.admin import APIKey

from aw.model.api import AwAPIKey
from aw.model.job import Job, JobExecution, JobExecutionResult, JobError, JobExecutionResultHost
from aw.model.permission import JobPermission, JobPermissionMemberUser, JobPermissionMemberGroup, \
    JobPermissionMapping
from aw.model.job_credential import JobGlobalCredentials, JobUserCredentials


admin.site.unregister(APIKey)

admin.site.register(Job)
admin.site.register(JobExecution)
admin.site.register(JobPermission)
admin.site.register(JobPermissionMemberUser)
admin.site.register(JobPermissionMemberGroup)
admin.site.register(JobPermissionMapping)
admin.site.register(JobExecutionResult)
admin.site.register(JobExecutionResultHost)
admin.site.register(JobError)
admin.site.register(JobGlobalCredentials)
admin.site.register(JobUserCredentials)
admin.site.register(AwAPIKey)
