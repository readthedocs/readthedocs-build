import os

from ..config import BuildConfig
from ..config import ProjectConfig


def get_project_config(build_config):
    bcs = [
        BuildConfig(
            build_config,
            source_file=str(os.path.join(os.getcwd(), 'readthedocs.yml')),
            source_position=0)]
    config = ProjectConfig(bcs)
    config.validate()
    return config
