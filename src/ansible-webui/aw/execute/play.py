import traceback

from ansible_runner import run as ansible_run

from aw.model.job import Job, JobExecution
from aw.execute.util import runner_cleanup, runner_prep, parse_run_result, job_logs, failure
from aw.utils.handlers import AnsibleConfigError
from aw.utils.util import datetime_w_tz, is_null


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime_w_tz()
    if is_null(execution):
        execution = JobExecution(user=None, job=job, comment='Scheduled')

    try:
        opts = runner_prep(job=job, execution=execution)
        logs = job_logs(job=job, execution=execution)

    except (OSError, AnsibleConfigError) as err:
        tb = traceback.format_exc(limit=1024)
        failure(execution=execution, time_start=time_start, error_s=err, error_m=tb)
        raise

    with (open(logs['stdout'], 'w', encoding='utf-8') as stdout,
          open(logs['stderr'], 'w', encoding='utf-8') as stderr):
        result = ansible_run(
            **opts,
            runner_mode='subprocess',
            output_fd=stdout,
            error_fd=stderr,
        )

    parse_run_result(
        time_start=time_start,
        execution=execution,
        result=result,
    )

    runner_cleanup(opts)
