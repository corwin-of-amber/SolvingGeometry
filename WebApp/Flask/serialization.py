import json
from sympy import Point2D


def json_custom(o):
    def fallback(o):
        if hasattr(o, '__json__'):
            return o.__json__()
        else:
            return SER_EXT.get(type(o), str)(o)
    return json.dumps(o, default=fallback)


def _ser(type_name, d):
    return {'$type': type_name, **d}

SER_EXT = {
    Point2D: lambda p: _ser('Point2D', {'x': p.x, 'y': p.y})
}