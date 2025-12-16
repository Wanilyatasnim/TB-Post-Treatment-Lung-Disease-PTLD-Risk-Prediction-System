from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def build_filter_url(context, **kwargs):
    """
    Build a filter URL preserving existing query parameters and updating specified ones.
    
    Usage:
        {% build_filter_url sex='M' %}
    """
    request = context['request']
    query_dict = request.GET.copy()
    
    # Update with new parameters
    for key, value in kwargs.items():
        if value is None or value == '':
            # Remove parameter if value is None or empty
            query_dict.pop(key, None)
        else:
            query_dict[key] = value
    
    # Remove page parameter when filtering (unless it's explicitly set)
    if 'page' not in kwargs:
        query_dict.pop('page', None)
    
    return '?' + query_dict.urlencode() if query_dict else ''

