from django import template

from aw.config.hardcoded import VERSION


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


# @register.filter
# def format_ts(datetime_obj):
#     return datetime.strftime(datetime_obj, config.DATETIME_TS_FORMAT)


# @register.simple_tag
# def random_gif() -> str:
#     return f"img/500/{randint(1, 20)}.gif"
