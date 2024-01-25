from django import template

from aw.model.job import JobExecution, CHOICES_JOB_EXEC_STATUS
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.utils.util import datetime_from_db, is_null

register = template.Library()


def _execution_info(execution: JobExecution) -> dict:
    base = {
        'user': f'by {execution.user.username}' if execution.user is not None else 'Scheduled',
        'status': CHOICES_JOB_EXEC_STATUS[execution.status][1],
        'time_start': datetime_from_db(execution.created).strftime(SHORT_TIME_FORMAT),
    }

    if execution.result is not None and execution.result.error is not None:
        error_m = ''
        if execution.result.error.med is not None:
            error_m = f"<br><b>Error full</b>:<div class=\"code\">{execution.result.error.med}</div>"

        logfile = execution.result.error.logfile
        if is_null(logfile):
            logfile = ''
        else:
            logfile = f"<br><b>Logfile</b>: <a href=file://{logfile}>{logfile}</a>"

        return {
            'time_start': datetime_from_db(execution.result.time_start).strftime(SHORT_TIME_FORMAT),
            'time_fin': datetime_from_db(execution.result.time_fin).strftime(SHORT_TIME_FORMAT),
            'failed': execution.result.failed,
            'error_s': execution.result.error.short,
            'error_m': error_m,
            'error_l': logfile,
            **base,
        }

    if execution.result is not None:
        return {
            'time_start': datetime_from_db(execution.result.time_start).strftime(SHORT_TIME_FORMAT),
            'time_fin': datetime_from_db(execution.result.time_fin).strftime(SHORT_TIME_FORMAT),
            'failed': execution.result.failed,
            **base,
        }

    return {
        'time_fin': 'Unknown',
        'failed': 'Unknown',
        **base,
    }


@register.filter
def execution_info_brief(execution: JobExecution) -> (str, None):
    if is_null(execution):
        return None

    info = _execution_info(execution)
    return (f"{info['time_start']}<br>{info['user']}<br><div class=\"aw-job-status "
            f"aw-job-status-{info['status'].lower()}\">{info['status']}</div>")


@register.filter
def execution_info_verbose(execution: JobExecution) -> (str, None):
    if is_null(execution):
        return None

    info = _execution_info(execution)

    if execution.result is not None and execution.result.error is not None:
        error = f"<br><br><b>Error</b>: <code>{info['error_s']}</code>{info['error_m']}{info['error_l']}"
    else:
        error = ''

    return (f"<hr><b>Start time</b>: {info['time_start']}<br><b>Finish time</b>: {info['time_fin']}<br>"
            f"<b>Executed by</b> '{info['user']}'<br><b>Status</b>: "
            f"<span class=\"aw-job-status aw-job-status-{info['status'].lower()}\">{info['status']}</span>{error}")
