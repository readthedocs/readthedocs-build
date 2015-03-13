import sys
import os
import subprocess
import tempfile

from doc_builder.loader import loading
from doc_builder.state import BuildState


def arg_to_option(arg):
    """
    Convert command line arguments into two-tuples of config key/value pairs.
    """
    arg = arg.lstrip('--')
    option = True
    if '=' in arg:
        arg, option = arg.split('=', 1)
    return (arg.replace('-', '_'), option)


def run_main():
    """
    Invokes main() with the contents of sys.argv
    This is a separate function so it can be invoked
    by a setuptools console_script.
    """
    opts = [arg_to_option(arg) for arg in sys.argv[1:] if arg.startswith('--')]
    try:
        main(args=sys.argv[1:], options=dict(opts))
    except Exception as e:
        print e.args[0]


def main(args, options=None):
    output_path = options.get('output', 'readthedocs_build')
    print "Building docs to " + output_path
    full = options.get('full', False)

    if full:
        temp = env = True
    else:
        temp = options.get('temp', False)
        env = options.get('env', False)

    if temp:
        docs_dir = tempfile.mkdtemp()
        repo_url = 'file://' + subprocess.check_output('git rev-parse --show-toplevel', shell=True).strip()
        state = BuildState(root=docs_dir, repo=repo_url, output_path=output_path)
    else:
        docs_dir = os.getcwd()
        state = BuildState(root=docs_dir, output_path=output_path)

    BuilderClass = loading.get('sphinx')
    builder = BuilderClass(state=state)

    if temp:
        print "Checking out code to %s" % docs_dir 
        builder.checkout_code()
    if env:
        print "Setting up virtualenv"
        builder.setup_environment()
    builder.append_conf()
    builder.build()
