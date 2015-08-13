from .virtualenv import VirtualEnv


class BaseBuilder(object):
    def __init__(self, build_config):
        self.build_config = build_config

    def setup(self):
        self.venv = VirtualEnv()

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
