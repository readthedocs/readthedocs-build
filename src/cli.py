import sys
import os
import subprocess
import tempfile
import webbrowser

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
    main(args=sys.argv[1:], options=dict(opts))


def main(args, options=None):
    """
    Processes build specific options.
    Uses a readthedocs.yml file to specify build-time settings.

    :param: output - Where files get rendered
    :param: full - Do a full build, creating a temp directory and use a virtualenv
    :param: config - Where the readthedocs.yml config is located

    """
    output_path = options.get('output', os.path.join(os.getcwd(), 'readthedocs_build'))
    full = options.get('full', False)
    _open = options.get('open', False)
    config = options.get('config', None)

    if full:
        temp = env = True
    else:
        temp = options.get('temp', False)
        env = options.get('env', False)

    # Read file config
    if config:
        print "Using config %s" % config
        state = BuildState.from_build_state(config)
    else:
        state = BuildState(root=os.getcwd())
        matches = state.full_find('readthedocs.yml')
        if len(matches) == 1:
            print "Using config %s" % matches[0]
            state = BuildState.from_build_state(matches[0])
        elif len(matches) > 1:
            print "ERROR: Multiple config files found: "
            print matches.join('\n')
            sys.exit(1)
        else:
            print "No configuration file given, using defaults"

    if temp:
        docs_dir = tempfile.mkdtemp()
        repo_url = 'file://' + subprocess.check_output('git rev-parse --show-toplevel', shell=True).strip()
        state.docs_dir = docs_dir
        state.repo_url = repo_url
        #state = BuildState(root=docs_dir, repo=repo_url, output_path=output_path)
    # else:
    #     docs_dir = os.getcwd()
    #     state = BuildState(root=docs_dir, output_path=output_path)


    # State keeping
    os.chdir(state.ROOT_URLCONF = '')
    state.output_path = output_path

    BuilderClass = loading.get('sphinx')
    builder = BuilderClass(state=state)

    print "Building docs to " + output_path

    if temp:
        print "Checking out code to %s" % docs_dir
        builder.checkout_code()
    if env:
        print "Setting up virtualenv"
        builder.setup_environment()
    try:
        builder.append_conf()
        builder.build()
    finally:
        builder.clean_conf()

    if _open:
        to_open = 'file://' + os.path.join(docs_dir, state.output_path, 'index.html')
        print "Opening %s" % to_open
        webbrowser.open(to_open)
