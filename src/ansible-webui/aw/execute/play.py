from datetime import datetime
from ansible_runner import run as ansible_run

from aw.model.job import Job, JobExecution
from aw.execute.util import runner_cleanup, runner_prep, parse_run_result, job_logs


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime.now()
    opts = runner_prep(job=job, execution=execution)
    logs = job_logs(job=job, execution=execution)

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
