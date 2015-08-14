from contextlib import contextmanager
import re
import os

from .find import find_all
from .parser import ParseError
from .parser import parse
from .validation import validate_bool
from .validation import validate_choice
from .validation import validate_directory
from .validation import validate_file
from .validation import ValidationError


__all__ = (
    'load', 'BuildConfig', 'ConfigError', 'InvalidConfig', 'ProjectConfig')


CONFIG_FILENAME = 'readthedocs.yml'


BASE_INVALID = 'base-invalid'
BASE_NOT_A_DIR = 'base-not-a-directory'
CONFIG_SYNTAX_INVALID = 'config-syntax-invalid'
CONFIG_REQUIRED = 'config-required'
NAME_REQUIRED = 'name-required'
NAME_INVALID = 'name-invalid'
TYPE_REQUIRED = 'type-required'
PYTHON_INVALID = 'python-invalid'


class ConfigError(Exception):
    def __init__(self, message, code):
        self.code = code
        super(ConfigError, self).__init__(message)


class InvalidConfig(ConfigError):
    message_template = 'Invalid "{key}": {error}'

    def __init__(self, key, code, error_message, source_file=None,
                 source_position=None):
        self.key = key
        self.code = code
        self.source_file = source_file
        self.source_position = source_position
        message = self.message_template.format(
            key=key,
            code=code,
            error=error_message)
        super(InvalidConfig, self).__init__(message, code=code)


class BuildConfig(dict):
    """
    Config that handles the build of one particular documentation. Config keys
    can be accessed with a dictionary lookup::

        >>> build_config['type']
        'sphinx'

    You need to call ``validate`` before the config is ready to use. Also
    setting the ``output_base`` is required before using it for a build.
    """

    BASE_INVALID_MESSAGE = 'Invalid value for base: {base}'
    BASE_NOT_A_DIR_MESSAGE = '"base" is not a directory: {base}'
    NAME_REQUIRED_MESSAGE = 'Missing key "name"'
    NAME_INVALID_MESSAGE = (
        'Invalid name "{name}". Valid values must match {name_re}')
    TYPE_REQUIRED_MESSAGE = 'Missing key "type"'
    PYTHON_INVALID_MESSAGE = '"python" section must be a mapping.'

    def __init__(self, env_config, raw_config, source_file, source_position):
        self.env_config = env_config
        self.raw_config = raw_config
        self.source_file = source_file
        self.source_position = source_position

    def error(self, key, message, code):
        source = '{file} [{pos}]'.format(
            file=self.source_file,
            pos=self.source_position)
        raise InvalidConfig(
            key=key,
            code=code,
            error_message='{source}: {message}'.format(source=source, message=message),
            source_file=self.source_file,
            source_position=self.source_position)

    @contextmanager
    def catch_validation_error(self, key):
        try:
            yield
        except ValidationError as error:
            raise InvalidConfig(
                key=key,
                code=error.code,
                error_message=error.message,
                source_file=self.source_file,
                source_position=self.source_position)

    def get_valid_types(self):
        return (
            'sphinx',
        )

    def validate(self):
        """
        Validate and process config into ``config`` attribute that contains the
        ready to use build configuration.

        It makes sure that:

        - ``type`` is set and is a valid builder
        - ``base`` is a valid directory and defaults to the directory of the
          ``readthedocs.yml`` config file if not set
        """

        # Validate env_config.
        self.validate_output_base()

        # Validate raw_config. Order matters.
        self.validate_name()
        self.validate_type()
        self.validate_base()
        self.validate_python()

    def validate_output_base(self):
        assert 'output_base' in self.env_config, (
            '"output_base" required in "env_config"')
        self['output_base'] = os.path.abspath(self.env_config['output_base'])

    def validate_name(self):
        name = self.raw_config.get('name', None)
        if not name:
            self.error('name', self.NAME_REQUIRED_MESSAGE, code=NAME_REQUIRED)
        name_re = r'^[-_.0-9a-zA-Z]+$'
        if not re.match(name_re, name):
            self.error(
                'name',
                self.NAME_INVALID_MESSAGE.format(
                    name=name,
                    name_re=name_re),
                code=NAME_INVALID)

        self['name'] = name

    def validate_type(self):
        if 'type' not in self.raw_config:
            self.error('type', self.TYPE_REQUIRED_MESSAGE, code=TYPE_REQUIRED)

        type = self.raw_config['type']
        with self.catch_validation_error('type'):
            validate_choice(type, self.get_valid_types())

        self['type'] = type

    def validate_base(self):
        if 'base' in self.raw_config:
            base = self.raw_config['base']
        else:
            base = os.path.dirname(self.source_file)
        with self.catch_validation_error('base'):
            base_path = os.path.dirname(self.source_file)
            base = validate_directory(base, base_path)
        self['base'] = base

    def validate_python(self):
        python = {
            'use_system_site_packages': False,
            'setup_py_install': False,
            'setup_py_path': os.path.join(
                os.path.dirname(self.source_file),
                'setup.py'),
        }

        if 'python' in self.raw_config:
            raw_python = self.raw_config['python']
            if not isinstance(raw_python, dict):
                self.error(
                    'python',
                    self.PYTHON_INVALID_MESSAGE,
                    code=PYTHON_INVALID)

            # Validate use_system_site_packages.
            if 'use_system_site_packages' in raw_python:
                with self.catch_validation_error(
                        'python.use_system_site_packages'):
                    python['use_system_site_packages'] = validate_bool(
                        raw_python['use_system_site_packages'])

            # Validate setup_py_install.
            if 'setup_py_install' in raw_python:
                with self.catch_validation_error('python.setup_py_install'):
                    python['setup_py_install'] = validate_bool(
                        raw_python['setup_py_install'])

            # Validate setup_py_path.
            if 'setup_py_path' in raw_python:
                with self.catch_validation_error('python.setup_py_path'):
                    base_path = os.path.dirname(self.source_file)
                    python['setup_py_path'] = validate_file(
                        raw_python['setup_py_path'], base_path)

        self['python'] = python


class ProjectConfig(list):
    """
    Wrapper for multiple build configs.
    """

    def validate(self):
        for build in self:
            build.validate()

    def set_output_base(self, directory):
        for build in self:
            build['output_base'] = os.path.abspath(directory)


def load(path, env_config):
    """
    Load a project configuration and all the contained build configs for a
    given path. That is usually the root of the project.

    The config will be validated.
    """

    config_files = list(find_all(path, CONFIG_FILENAME))
    if not config_files:
        raise ConfigError(
            'No {filename} found'.format(filename=CONFIG_FILENAME),
            code=CONFIG_REQUIRED)
    build_configs = []
    for filename in config_files:
        with open(filename, 'r') as file:
            try:
                configs = parse(file.read())
            except ParseError as error:
                raise ConfigError(
                    'Parse error in {filename}: {message}'.format(
                        filename=filename,
                        message=error.message),
                    code=CONFIG_SYNTAX_INVALID)
            for i, config in enumerate(configs):
                build_config = BuildConfig(
                    env_config,
                    config,
                    source_file=filename,
                    source_position=i)
                build_configs.append(build_config)

    project_config = ProjectConfig(build_configs)
    project_config.validate()
    return project_config
