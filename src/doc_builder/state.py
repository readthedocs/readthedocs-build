import fnmatch
import json
import yaml
import os
import re
import logging

from vcs_support.base import VCSProject
from vcs_support.backends import backend_cls
from doc_builder.constants import BuildException


log = logging.getLogger(__name__)


class VersionMixin(object):

    def get_doc_path(self):
        """
        The path to the documentation root in the project.
        """
        for possible_path in ['docs', 'doc', 'Doc']:
            full_possible_path = os.path.join(
                self.root, '%s' % possible_path)
            if os.path.exists(full_possible_path):
                return full_possible_path
        return self.root

    def find(self, file):
        """
        Find a file inside of the doc checkout.
        """
        matches = []
        for root, dirnames, filenames in os.walk(self.get_doc_path()):
            for filename in fnmatch.filter(filenames, file):
                matches.append(os.path.join(root, filename))
        return matches

    def full_find(self, file):
        """
        Find a file inside the full doc root
        """
        matches = []
        for root, dirnames, filenames in os.walk(self.root):
            for filename in fnmatch.filter(filenames, file):
                matches.append(os.path.join(root, filename))
        return matches

    @property
    def conf_file(self):
        files = self.find('conf.py')
        if not files:
            files = self.full_find('conf.py')
        if len(files) == 1:
            return files[0]
        elif len(files) > 1:
            for file in files:
                if file.find('doc', 70) != -1:
                    return file
        else:
            # Having this be translatable causes this odd error:
            # ProjectImportError(<django.utils.functional.__proxy__ object at
            # 0x1090cded0>,)
            raise BuildException(
                u"Conf File Missing. Please make sure you have a conf.py in your project."
            )

    @property
    def conf_dir(self):
        if self.conf_file:
            return self.conf_file.replace('/conf.py', '')

    def env_bin(self, bin):
        return os.path.join(self.env_path, 'bin', bin)


class VCSMixin(object):

    @property
    def username_repo(self):
        if 'github' in self.repo:
            matches = self.GH_REGEXS
            self.display_github = True
        elif 'bitbucket' in self.repo:
            matches = self.BB_REGEXS
            self.display_bitbucket = True
        for regex in matches:
            match = regex.search(self.repo)
            if match:
                return match.groups()
        return (None, None)

    def vcs_repo(self, name, root):
        backend = backend_cls.get(self.type)
        if not backend:
            repo = None
        else:
            proj = VCSProject(name, self.commit, root, self.repo)
            repo = backend(proj)
        return repo


class BuildState(VCSMixin, VersionMixin):

    """
    An object that maintains the state for the build happening on Read the Docs.

    It's tied to a specific version,
    and will either come from a YAML file in the repo,
    or from the database.
    """

    root = None
    project = None
    version = None

    # VCS
    repo = None
    type = 'git'
    commit = ''

    language = 'en'
    downloads = []
    versions = []
    analytics_code = None
    canonical_url = None
    single_version = None

    virtualenv = True
    interpreter = 'python2'
    system_packages = False
    allow_comments = False
    use_system_packages = False

    documentation_type = 'sphinx'
    requirements_file = ''
    config_path = ''
    build_types = ['html', 'pdf', 'epub']

    # Settings
    API_HOST = 'https://readthedocs.org'
    MEDIA_URL = 'https://media.readthedocs.org/'
    PRODUCTION_DOMAIN = 'https://readthedocs.org'
    STATIC_PATH = '/static/'
    TEMPLATE_PATH = None
    REPO_LOCK_SECONDS = 30
    HTML_ONLY = []

    def __init__(self, root, **kwargs):
        self.root = root

        for kwarg, val in kwargs.items():
            setattr(self, kwarg, val)

        self.env_path = os.path.join(root, 'venv')

    def get_build_state(self, path):
        """
        Generate the build state for a version.
        """
        log.debug("Checking for json config")
        try:
            rtd_yaml = open(path)
            yaml_obj = yaml.load(rtd_yaml)
            for key in yaml_obj.keys():
                # Treat the defined fields on self as
                # the canonical list of allowed user editable fields.
                if key not in self.__dict__:
                    del yaml_obj[key]
            log.debug("Updated from JSON.")
        except IOError:
            log.debug("No .readthedocs.yml found.")
        return self.__class__(**yaml_obj)

