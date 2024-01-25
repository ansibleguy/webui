import traceback

from ansible_runner import RunnerConfig, Runner

from aw.model.job import Job, JobExecution
from aw.execute.play_util import runner_cleanup, runner_prep, parse_run_result, job_logs, failure
from aw.execute.util import get_path_run
from aw.utils.util import datetime_w_tz, is_null
from aw.utils.handlers import AnsibleConfigError


class AwRunnerConfig(RunnerConfig):
    def __init__(self, stdout, stderr, **kwargs):
        super().__init__(**kwargs)
        self.runner_mode = 'subprocess'
        self.output_fd = stdout
        self.stderr = stderr


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime_w_tz()
    path_run = get_path_run()
    if is_null(execution):
        execution = JobExecution(user=None, job=job, comment='Scheduled')

    try:
        opts = runner_prep(job=job, execution=execution, path_run=path_run)
        logs = job_logs(job=job, execution=execution)

        with (open(logs['stdout'], 'w', encoding='utf-8') as stdout,
              open(logs['stderr'], 'w', encoding='utf-8') as stderr):

            config = AwRunnerConfig(
                stdout=stdout,
                stderr=stderr,
                **opts
            )

            config.prepare()
            runner = Runner(config=config)
            runner.run()

            parse_run_result(
                time_start=time_start,
                execution=execution,
                runner=runner,
            )
            del runner

        runner_cleanup(path_run)

    except (OSError, AnsibleConfigError) as err:
        tb = traceback.format_exc(limit=1024)
        failure(
            execution=execution, path_run=path_run, time_start=time_start,
            error_s=str(err), error_m=tb
        )
        raise
