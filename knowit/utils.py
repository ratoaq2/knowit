import os
import sys
import typing

from knowit import VIDEO_EXTENSIONS

if sys.version_info < (3, 8):
    OS_FAMILY = str
else:
    OS_FAMILY = typing.Literal['windows', 'macos', 'unix']

OPTION_MAP = typing.Dict[str, typing.Tuple[str]]


def recurse_paths(
        paths: typing.Union[str, typing.Iterable[str]]
) -> typing.List[str]:
    """Return a list of video files."""
    enc_paths = []

    if isinstance(paths, str):
        paths = [p.strip() for p in paths.split(',')] if ',' in paths else paths.split()

    for path in paths:
        if os.path.isfile(path):
            enc_paths.append(path)
        if os.path.isdir(path):
            for root, directories, filenames in os.walk(path):
                for filename in filenames:
                    if os.path.splitext(filename)[1] in VIDEO_EXTENSIONS:
                        full_path = os.path.join(root, filename)
                        enc_paths.append(full_path)

    # Lets remove any dupes since mediainfo is rather slow.
    unique_paths = dict.fromkeys(enc_paths)
    return list(unique_paths)


def to_dict(
        obj: typing.Any,
        classkey: typing.Optional[typing.Type] = None
) -> typing.Union[str, dict, list]:
    """Transform an object to dict."""
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v, classkey)
        return data
    elif hasattr(obj, '_ast'):
        return to_dict(obj._ast())
    elif hasattr(obj, '__iter__'):
        return [to_dict(v, classkey) for v in obj]
    elif hasattr(obj, '__dict__'):
        values = [(key, to_dict(value, classkey))
                  for key, value in obj.__dict__.items() if not callable(value) and not key.startswith('_')]
        data = {k: v for k, v in values if v is not None}
        if classkey is not None and hasattr(obj, '__class__'):
            data[classkey] = obj.__class__.__name__
        return data
    return obj


def detect_os() -> OS_FAMILY:
    """Detect os family: windows, macos or unix."""
    if os.name in ('nt', 'dos', 'os2', 'ce'):
        return 'windows'
    if sys.platform == 'darwin':
        return 'macos'
    return 'unix'


def define_candidate(
        locations: OPTION_MAP,
        names: OPTION_MAP,
        os_family: typing.Optional[OS_FAMILY] = None,
        suggested_path: typing.Optional[str] = None,
) -> typing.Generator[str, None, None]:
    """Generate candidate list for the given parameters."""
    os_family = os_family or detect_os()
    for location in (suggested_path, ) + locations[os_family]:
        if not location:
            continue

        if location == '__PATH__':
            for name in names[os_family]:
                if os_family == 'windows':
                    for path in os.environ['PATH'].split(';'):
                        yield os.path.join(path, name)
                else:
                    yield name
        elif os.path.isfile(location):
            yield location
        elif os.path.isdir(location):
            for name in names[os_family]:
                cmd = os.path.join(location, name)
                if os.path.isfile(cmd):
                    yield cmd
