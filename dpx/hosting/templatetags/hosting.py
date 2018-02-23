from django.template import Library

register = Library()


@register.simple_tag(takes_context=True)
def download_url(context, obj):
    return obj.get_download_url(
        context['request']
    )
