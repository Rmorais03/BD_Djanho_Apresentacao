from django import template

register = template.Library()

@register.filter
def getattr(obj, args):
    """Try to get an attribute from an object. Example: {{ item|getattr:"name" }}"""
    if obj is None:
        return None
        
    # Handle nested lookups like "company.name"
    if '.' in str(args):
        parts = str(args).split('.')
        current = obj
        for part in parts:
            if current is None:
                return None
            try:
                current = current.__getattribute__(part)
            except AttributeError:
                try:
                    # Could be a dict
                    current = current.get(part)
                except AttributeError:
                    return None
        return current

    # Handle simple lookups
    try:
        return obj.__getattribute__(args)
    except AttributeError:
        try:
            return obj.get(args)
        except AttributeError:
            return None

@register.filter
def replace(value, args):
    """Replace occurrences. Usage: {{ value|replace:'old' }}
    Replaces 'old' with empty string. For old,new use: {{ value|replace:'old,new' }}"""
    if value is None:
        return ''
    value = str(value)
    if ',' in args:
        old, new = args.split(',', 1)
    else:
        old = args
        new = ''
    return value.replace(old, new)

@register.filter
def is_bool(value):
    """Returns True if the value is a boolean, False otherwise."""
    return isinstance(value, bool)
