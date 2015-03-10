import os
import subprocess
import traceback
import logging


log = logging.getLogger(__name__)


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

    for command in commands:
        if shell:
            log.info("Running commands in a shell")
            run_command = command
        else:
            run_command = command.split()
        log.info("Running: '%s' [%s]" % (command, cwd))
        try:
            p = subprocess.Popen(run_command, shell=shell, cwd=cwd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, env=environment)

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

