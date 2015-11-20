import os

from .virtualenv import VirtualEnv


class BaseBuilder(object):
    python_dependencies = ()

    def __init__(self, build_config):
        self.build_config = build_config

    def get_source_directory(self):
        return self.build_config['base']

    def setup(self):
        self.setup_virtualenv()

    def setup_virtualenv(self):
        python_config = self.build_config['python']
        use_system_site_packages = python_config['use_system_site_packages']
        self.venv = VirtualEnv(system_site_packages=use_system_site_packages)
        for package in self.python_dependencies:
            self.venv.install(package)
        if python_config['setup_py_install']:
            setup_py_path = python_config['setup_py_path']
            self.venv.python_run(setup_py_path, ['install'])

    def get_output_directory(self, format):
        out_dir = os.path.join(
            self.build_config['output_base'],
            self.build_config['name'],
            format)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        return out_dir

    def build(self):
        """
        Initializes the build.
        """
        self.setup()
        self.build_html()
        self.build_search_data()
        self.cleanup()

    def build_html(self):
        # Must be overriden by subclass.
        pass

    def build_search_data(self):
        """
        Subclasses should override this method and build search data in a JSON
        format in the ``search_data`` output directory.
        """
        # Must be overriden by subclass.
        pass

    def cleanup(self):
        self.venv.cleanup()
