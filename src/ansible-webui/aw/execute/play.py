import traceback

from ansible_runner import RunnerConfig, Runner

from aw.model.job import Job, JobExecution
from aw.execute.play_util import runner_cleanup, runner_prep, parse_run_result, failure
from aw.execute.util import get_path_run, write_stdout_stderr
from aw.utils.util import datetime_w_tz, is_null  # get_ansible_versions
from aw.utils.handlers import AnsibleConfigError
from aw.utils.debug import log


class AwRunnerConfig(RunnerConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runner_mode = 'subprocess'


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime_w_tz()
    path_run = get_path_run()
    if is_null(execution):
        execution = JobExecution(user=None, job=job, comment='Scheduled')

    def _cancel_job() -> bool:
        return job.state_stop

    runner_cfg = None
    try:
        opts = runner_prep(job=job, execution=execution, path_run=path_run)

        # todo: fix runner overwriting pre-run logs
        runner_cfg = AwRunnerConfig(**opts)
        # write_stdout_stderr(config=config, msg=f"VERSIONS: '{get_ansible_versions()}'")
        runner_cfg.prepare()
        log(msg=f"Running job '{job.name}': '{' '.join(runner_cfg.command)}'", level=5)
        # write_stdout_stderr(config=config, msg=f"RUNNING COMMAND: '{' '.join(config.command)}'")

        runner = Runner(config=runner_cfg, cancel_callback=_cancel_job)
        runner.run()

        write_stdout_stderr(cfg=runner_cfg, msg='PROCESSING RESULT')
        parse_run_result(
            time_start=time_start,
            execution=execution,
            runner=runner,
        )
        del runner

        write_stdout_stderr(cfg=runner_cfg, msg='CLEANUP')
        runner_cleanup(job=job, execution=execution, path_run=path_run, cfg=runner_cfg)

    except (OSError, AnsibleConfigError) as err:
        tb = traceback.format_exc(limit=1024)
        failure(
            job=job, execution=execution, path_run=path_run, time_start=time_start,
            error_s=str(err), error_m=tb, cfg=runner_cfg,
        )
        raise
