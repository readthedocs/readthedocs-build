from .base import BaseBuilder


class SphinxBuilder(BaseBuilder):
    """
    TODO:

    - Build HTML
    - Build HTML in htmldir format
    - Build HTML in singlefile format
    - Build PDF
    - Build ePUB
    """

    python_dependencies = BaseBuilder.python_dependencies + (
        'Sphinx==1.3.1',
    )

    def build_html(self):
        raise NotImplementedError('TODO')
