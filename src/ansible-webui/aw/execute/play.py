from datetime import datetime
from ansible_runner import run as ansible_run

from aw.model.job import Job, JobExecution
from aw.execute.util import runner_cleanup, runner_prep, parse_run_result


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime.now()
    opts = runner_prep(job=job, execution=execution)

    result = ansible_run(**opts)

    parse_run_result(
        time_start=time_start,
        execution=execution,
        result=result,
    )

    runner_cleanup(opts)
