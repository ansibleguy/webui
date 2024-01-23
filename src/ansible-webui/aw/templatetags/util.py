from django import template

from aw.config.main import VERSION
from aw.config.navigation import NAVIGATION
from aw.model.job import JobExecution, CHOICES_JOB_EXEC_STATUS
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.utils.util import datetime_from_db, is_null


register = template.Library()


@register.simple_tag
def get_version() -> str:
    return VERSION


@register.simple_tag
def set_var(val):
    return val


@register.filter
def get_full_uri(request):
    return request.build_absolute_uri()


@register.filter
def get_nav(key: str) -> dict:
    # serves navigation config to template
    return NAVIGATION[key]


@register.filter
def get_type(value):
    return str(type(value)).replace("<class '", '').replace("'>", '')


@register.filter
def get_value(data: dict, key: (str, int)):
    if hasattr(data, 'get'):
        return data.get(key, None)

    if hasattr(data, key):
        return getattr(data, key)

    return None


@register.filter
def get_fallback(data, fallback):
    return data if data not in [None, ''] else fallback


@register.filter
def exists(data: (dict, list, str, bool)) -> bool:
    if data is None:
        return False

    if isinstance(data, bool):
        return data

    if isinstance(data, (list, dict)):
        return len(data) > 0

    if isinstance(data, str):
        return data.strip() != ''

    return False


@register.filter
def get_choice(choices: list[tuple[int, any]], idx: int):
    return choices[idx][1]


@register.filter
def to_dict(data):
    return data.__dict__


@register.filter
def ignore_none(data):
    if data is None:
        return ''

    return data


def _execution_info(execution: JobExecution) -> dict:
    base = {
        'user': f'by {execution.user.username}' if execution.user is not None else 'Scheduled',
        'status': CHOICES_JOB_EXEC_STATUS[execution.status][1],
        'time_start': datetime_from_db(execution.created).strftime(SHORT_TIME_FORMAT),
    }
    if execution.result is not None:
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

    return {
        'time_fin': 'Unknown',
        'failed': 'Unknown',
        'error_s': 'None',
        'error_m': '',
        'error_l': '',
        **base,
    }


@register.filter
def execution_info_brief(execution: JobExecution) -> (str, None):
    if execution is None:
        return None

    info = _execution_info(execution)
    return (f"{info['time_start']}<br>{info['user']}<br><div class=\"aw-job-status "
            f"aw-job-status-{info['status'].lower()}\">{info['status']}</div>")


@register.filter
def execution_info_verbose(execution: JobExecution) -> (str, None):
    if execution is None:
        return None

    info = _execution_info(execution)
    return (f"<hr><b>Start time</b>: {info['time_start']}<br><b>Finish time</b>: {info['time_fin']}<br>"
            f"<b>Executed by</b> '{info['user']}'<br><b>Status</b>: "
            f"<span class=\"aw-job-status aw-job-status-{info['status'].lower()}\">{info['status']}</span><br><br>"
            f"<b>Error</b>: <code>{info['error_s']}</code>{info['error_m']}{info['error_l']}")
