# -*- coding: utf-8 -*-


def todict(obj, classkey=None):
    """Transform an object to dict."""
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, '_ast'):
        return todict(obj._ast())
    elif hasattr(obj, '_iter__'):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, '__dict__'):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, '__class__'):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
