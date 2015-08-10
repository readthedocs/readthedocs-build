import sys
import os

from .utils import cd


def main(path=None):
    """
    Exit codes:

        0 -- success
        1 -- bad config
    """

    if path is None:
        path = os.getcwd()

    with cd(path):
        cwd = os.getcwd()
        config_path = os.path.join(cwd, 'readthedocs.yml')
        if not os.path.exists(config_path):
            sys.exit(1)
