from .virtualenv import VirtualEnv


class BaseBuilder(object):
    python_dependencies = ()

    def __init__(self, build_config):
        self.build_config = build_config

    def setup(self):
        self.setup_virtualenv()

    def setup_virtualenv(self):
        self.venv = VirtualEnv()
        for package in self.python_dependencies:
            self.venv.install(package)

    def build(self):
        """
        Initializes the build.
        """
        self.setup()
        self.build_html()
        self.cleanup()

    def build_html(self):
        # Must be overriden by subclass.
        pass

    def cleanup(self):
        self.venv.cleanup()
