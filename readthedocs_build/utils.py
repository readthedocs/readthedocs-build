import contextlib
import os


@contextlib.contextmanager
def cd(directory):
    """
    ::

        with cd(new_cwd):
            os.walk('.')
    """
    old_path = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(old_path)
