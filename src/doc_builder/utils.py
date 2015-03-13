import sys
import json
import os
import subprocess
import traceback
import logging
from cStringIO import StringIO

from sphinx.util.console import bold, lightgray, darkgray, darkgreen, red

log = logging.getLogger(__name__)


def restoring_chdir(fn):
    # XXX:dc: This would be better off in a neutral module
    @wraps(fn)
    def decorator(*args, **kw):
        try:
            path = os.getcwd()
            return fn(*args, **kw)
        finally:
            os.chdir(path)
    return decorator


def run(*commands, **kwargs):
    """
    Run one or more commands, and return ``(status, out, err)``.
    If more than one command is given, then this is equivalent to
    chaining them together with ``&&``; if all commands succeed, then
    ``(status, out, err)`` will represent the last successful command.
    If one command failed, then ``(status, out, err)`` will represent
    the failed command.
    """
    environment = os.environ.copy()
    environment['READTHEDOCS'] = 'True'
    if 'DJANGO_SETTINGS_MODULE' in environment:
        del environment['DJANGO_SETTINGS_MODULE']
    if 'PYTHONPATH' in environment:
        del environment['PYTHONPATH']
    cwd = os.getcwd()
    if not commands:
        raise ValueError("run() requires one or more command-line strings")
    shell = kwargs.get('shell', False)

    stdout = kwargs.get('stdout', subprocess.PIPE)
    stderr = kwargs.get('stderr', subprocess.STDOUT)

    for command in commands:
        if shell:
            log.info("Running commands in a shell")
            run_command = command
        else:
            run_command = command.split()
        log.info("Running: '%s' [%s]" % (command, cwd))
        print bold("$ '%s' [%s]" % (command, cwd))
        try:
            p = subprocess.Popen(run_command, shell=shell, cwd=cwd,
                                 stdout=stdout,
                                 stderr=stderr, env=environment)

            out, err = p.communicate()
            ret = p.returncode
        except:
            out = ''
            err = traceback.format_exc()
            ret = -1
            log.error("Command failed", exc_info=True)

    return (ret, out, err)


def safe_write(filename, contents):
    """Write ``contents`` to the given ``filename``. If the filename's
    directory does not exist, it is created. Contents are written as UTF-8,
    ignoring any characters that cannot be encoded as UTF-8.
    """
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, 'w') as fh:
        fh.write(contents.encode('utf-8', 'ignore'))
        fh.close()


def obj_to_json(obj):
    """Represent instance of a class as JSON.
    Arguments:
    obj -- any object
    Return:
    String that reprent JSON-encoded object.
    """
    def serialize(obj):
        """Recursively walk object's hierarchy."""
        if isinstance(obj, (bool, int, long, float, basestring)):
            return obj
        elif isinstance(obj, dict):
            obj = obj.copy()
            for key in obj:
                obj[key] = serialize(obj[key])
            return obj
        elif isinstance(obj, list):
            return [serialize(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(serialize([item for item in obj]))
        elif hasattr(obj, '__dict__'):
            return serialize(obj.__dict__)
        else:
            return repr(obj)  # Don't know how to handle, convert to string
    return json.dumps(serialize(obj))


class Capturing(list):

    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringio_out = StringIO()
        sys.stderr = self._stringio_err = StringIO()
        return self

    def __exit__(self, *args):
        self.extend([self._stringio_out.getvalue().splitlines(),
                     self._stringio_err.getvalue().splitlines(),
                     ])
        sys.stdout = self._stdout
        sys.stderr = self._stderr
