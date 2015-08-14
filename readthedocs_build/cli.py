import click
import os
import sys

from .build import build
from .config import load
from .config import ConfigError
from .utils import cd


@click.command()
@click.argument('path',
                required=False,
                type=click.Path(exists=True, file_okay=False, readable=True),
                default='.')
@click.option('--outdir',
              type=click.Path(file_okay=False, writable=True),
              default='_readthedocs_build',
              help='build output directory')
def main(path, outdir):
    """
    Exit codes:

        0 -- success
        1 -- bad config
    """

    if path is None:
        path = os.getcwd()

    env_config = {
        'output_base': outdir,
    }

    with cd(path):
        try:
            project_config = load(os.getcwd(), env_config)
        except ConfigError as error:
            sys.stderr.write('Error: {error}'.format(error=error))
            sys.exit(1)
        build(project_config)
